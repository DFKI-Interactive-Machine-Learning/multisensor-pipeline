from abc import ABC
import logging
from multisensor_pipeline.modules import BaseSource
from multisensor_pipeline.dataframe import MSPDataFrame, MSPControlMessage
from time import time, sleep

logger = logging.getLogger(__name__)


class BaseFixedRateSource(BaseSource, ABC):

    def __init__(self, sampling_rate: float = 1.):
        """
        Args:
            sampling_rate: set the intended samplerate in Hertz [Hz]
        """
        super().__init__()
        self._samplerate = sampling_rate
        self._sleep_time = 1. / self._samplerate

        self._t_last = None

    @property
    def sampling_rate(self):
        return self._samplerate

    def _notify(self, frame: MSPDataFrame):
        super(BaseFixedRateSource, self)._notify(frame)
        self._sleep(frame)

    def _sleep(self, frame: MSPDataFrame):
        if isinstance(frame, MSPControlMessage):
            return
        if self._samplerate == float("inf"):
            return

        # ignore processing time for the first frame, as we cannot compute it
        if self._t_last is None:
            sleep(self._sleep_time)
        # this is any frame after the first one
        else:
            t_now = time()
            t_processing = t_now - self._t_last

            # Default case: processing time takes a small portion of the required sleep time -> compensate for this
            if t_processing < self._sleep_time:
                sleep(self._sleep_time - t_processing)
            # In any other case, i.e., t_processing >= self._sleep_time, we don't sleep.
            # If the processing time is larger than the sleep time, the source will fail to deliver its samples on time
            elif t_processing > self._sleep_time:
                logger.warning(f"The processing time of {self.name} takes longer than required for the defined "
                               f"samplerate of {self._samplerate} Hz. Processing takes {t_processing} s.")

        # after this statement, the processing time for preparing the next frame begins
        self._t_last = time()
