from abc import ABC
from multisensor_pipeline.modules import BaseSource
from multisensor_pipeline.dataframe import MSPDataFrame, MSPControlMessage
from time import time, sleep


class BaseFixedRateSource(BaseSource, ABC):

    def __init__(self, sampling_rate: float = 1.):
        super().__init__()
        self._sampling_rate = sampling_rate
        self._sleep_time = 1. / self._sampling_rate  # FIXME: sampling_rate is not given in Hz

        self._last_frame_timestamp = None

    @property
    def sampling_rate(self):
        return self._sampling_rate

    def _notify(self, frame: MSPDataFrame):
        super(BaseFixedRateSource, self)._notify(frame)
        self._sleep(frame)

    def _sleep(self, frame: MSPDataFrame):
        if isinstance(frame, MSPControlMessage):
            return
        if self._sampling_rate == float("inf"):
            return

        if self._last_frame_timestamp is None:
            sleep(self._sleep_time)
        else:
            processing_duration = time() - self._last_frame_timestamp
            if processing_duration < self._sleep_time:
                sleep(self._sleep_time - processing_duration)

        self._last_frame_timestamp = time()
