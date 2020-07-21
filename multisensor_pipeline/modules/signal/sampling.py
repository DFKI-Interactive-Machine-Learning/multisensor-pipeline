from multisensor_pipeline import BaseProcessor
from multisensor_pipeline.utils.dataframe import MSPDataFrame
import logging


logger = logging.getLogger(__name__)


class DownsamplingProcessor(BaseProcessor):

    _dtype_in = None
    _sampling_rate = None
    _period_time = None

    _last_sample_sent = {}
    _last_sample_received = {}

    def __init__(self, dtype=None, sampling_rate=5):
        """
        Downsamples a signal to a given sampling_rate [Hz], if the original rate is higher.
        Otherwise, the sampling rate stays the same (no upsampling).
        @param dtype: the dtype to be resampled; if None, all incoming dtypes are resampled
        @param sampling_rate: the desired sampling rate [Hz]
        """
        super().__init__()
        self._dtype_in = dtype
        self._sampling_rate = sampling_rate
        self._period_time = 1. / sampling_rate

    def _handle_dataframe(self, dtype, dataframe: MSPDataFrame):
        if dtype not in self._last_sample_sent:
            self._notify_all(dtype, dataframe, suffix=f"{self._sampling_rate}Hz")
            self._last_sample_sent[dtype] = dataframe
            self._last_sample_received[dtype] = dataframe
            return

        timestamp = dataframe.timestamp
        last_sent_period_time = timestamp - self._last_sample_sent[dtype].timestamp
        last_received_period_time = timestamp - self._last_sample_received[dtype].timestamp
        if last_sent_period_time >= self._period_time:
            # send the sample that is closest to the optimal sampling timestamp (= last_timestamp + period_time)
            if abs(last_sent_period_time - self._period_time) <= abs(last_received_period_time - self._period_time):
                self._notify_all(dtype, dataframe, suffix=f"{self._sampling_rate}Hz")
                self._last_sample_sent[dtype] = dataframe
            else:
                self._notify_all(dtype, self._last_sample_received[dtype], suffix=f"{self._sampling_rate}Hz")
                self._last_sample_sent[dtype] = self._last_sample_received[dtype]
        self._last_sample_received[dtype] = dataframe

    def _update_loop(self):
        while self._active:
            dtype, dataframe = self.get()

            if dtype.endswith(b".eof"):
                # TODO: end of file workaround, shall be replaced by a proper EOF integration
                self._notify_all(dtype, dataframe)
                continue

            if dtype == self._dtype_in or self._dtype_in is None:
                self._handle_dataframe(dtype, dataframe)
