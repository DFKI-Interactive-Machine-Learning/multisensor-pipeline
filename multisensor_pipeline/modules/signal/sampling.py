from multisensor_pipeline import BaseProcessor
from multisensor_pipeline.utils.dataframe import MSPDataFrame
import logging
import numpy as np


logger = logging.getLogger(__name__)


class DownsamplingProcessor(BaseProcessor):

    class SampleHistory:

        def __init__(self, dtype, fps_out, window_size=5, interpolation=None):
            self.dtype = dtype
            self.target_fps = fps_out
            self.window_size = window_size  # TODO: expose window_size, mainly for interpolation
            self.interpolation = interpolation  # TODO: utilize interpolation for, e.g., averaging the data
            self.target_period_time = 1. / self.target_fps
            self.last_sent = None
            self.samples = []
            self._timestamps_out = []  # for fps estimation

        def add(self, sample):
            self.samples.append(sample)

        def _update_and_get_last_sample(self, sample_id):
            self.last_sent = self.samples[sample_id]
            # keep the last n timestamps for estimating actual frame-rate
            self._timestamps_out.append(self.last_sent.timestamp)
            if len(self._timestamps_out) > self.window_size:
                self._timestamps_out = self._timestamps_out[1:]
            # logger.info(f"{round(self.fps_out, 3)} fps (out)")
            # keep samples that arrived after the sent one
            self.samples = self.samples[sample_id + 1:]
            return self.last_sent

        def get_send_sample(self):
            assert len(self.samples) > 0, "there was no sample yet"

            # if nothing was sent before take first=last sample and reset the list
            if self.last_sent is None:
                assert len(self.samples) == 1, "if nothing was sent, there should be only one sample in the list"
                return self._update_and_get_last_sample(0)
            else:
                # check whether current sample shall be sent
                current_time = self.last_received.timestamp
                last_sent_time = self.last_sent.timestamp
                current_period_time = current_time - last_sent_time
                if current_period_time >= self.target_period_time:  # - self.current_delay:
                    # send sample that is closest to period time (+/- delay to keep up with target frame-rate)
                    recent_timestamps = np.array([s.timestamp for s in self.samples])
                    recent_time_diffs = np.fabs(recent_timestamps - last_sent_time - self.target_period_time)
                    sample_id = np.argmin(recent_time_diffs)
                    return self._update_and_get_last_sample(sample_id)

            return None

        @property
        def current_delay(self):
            """returns the deviation from the targeted period time"""
            return self.period_time_out - self.target_period_time

        @property
        def fps_out(self):
            return 1. / self.period_time_out

        @property
        def period_time_out(self):
            if len(self._timestamps_out) < self.window_size:
                return self.target_period_time
            else:
                period_time_estimate = (self._timestamps_out[-1] - self._timestamps_out[0]) / \
                                       (len(self._timestamps_out) - 1)
                return period_time_estimate

        @property
        def last_received(self):
            return self.samples[-1]

        @property
        def fps_in(self):
            return 1. / self.period_time_in

        @property
        def period_time_in(self):
            return (self.samples[-1].timestamp - self.samples[0].timestamp) / len(self.samples)

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

        self._sample_hist = dict()
        self._last_sent = dict()
        self._last_received = dict()

    def _send_sample(self, dtype, dataframe):
        self._notify_all(dtype, dataframe, suffix=f"{self._sampling_rate}Hz")
        self._last_sent[dtype] = dataframe

    def _get_history(self, dtype) -> SampleHistory:
        if dtype not in self._sample_hist:
            self._sample_hist[dtype] = self.SampleHistory(dtype, fps_out=self._sampling_rate)
        return self._sample_hist[dtype]

    def _handle_dataframe(self, dtype, dataframe: MSPDataFrame):
        hist = self._get_history(dtype)
        hist.add(dataframe)
        send_sample = hist.get_send_sample()
        if send_sample is not None:
            self._notify_all(dtype, send_sample, suffix=f"{self._sampling_rate}Hz")

    def _update(self, frame=None):
        while self._active:
            dtype, dataframe = self.get()

            if dtype.endswith(b".eof"):
                # TODO: end of file workaround, shall be replaced by a proper EOF integration
                self._notify_all(dtype, dataframe)
                continue

            if dtype == self._dtype_in or self._dtype_in is None:
                self._handle_dataframe(dtype, dataframe)
