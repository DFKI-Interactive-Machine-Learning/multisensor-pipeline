from abc import ABC
import json
from multisensor_pipeline.dataframe import MSPDataFrame, MSPControlMessage
from multisensor_pipeline.modules import BaseSource
from time import time, sleep


class BaseDatasetSource(BaseSource, ABC):

    def __init__(self, playback_speed: float = float("inf")):
        super().__init__()
        self._playback_speed = playback_speed
        self._last_original_timestamp = None
        self._last_playback_timestamp = None

    @property
    def playback_speed(self):
        return self._playback_speed

    def _notify(self, frame: MSPDataFrame):
        self._sleep(frame)
        frame['playback_timestamp'] = time()
        super(BaseDatasetSource, self)._notify(frame)

    def _sleep(self, frame):
        if isinstance(frame, MSPControlMessage):
            return
        if self._playback_speed == float("inf"):
            return

        if self._last_original_timestamp is not None:
            original_delta = frame.timestamp - self._last_original_timestamp
            target_delta = original_delta / self._playback_speed

            actual_delta = time() - self._last_playback_timestamp
            if actual_delta < target_delta:
                sleep(target_delta - actual_delta)

        self._last_original_timestamp = frame.timestamp
        self._last_playback_timestamp = time()


class JsonDatasetSource(BaseDatasetSource):

    def __init__(self, file_path, **kwargs):
        super(JsonDatasetSource, self).__init__(**kwargs)
        self._file_path = file_path
        self._file_handle = None

    def _start(self):
        self._file_handle = open(self._file_path, mode="r")

    def _update(self) -> MSPDataFrame:
        line = self._file_handle.readline()
        if line == '':
            # EOF is reached -> auto-stop
            self.stop(blocking=False)
            return MSPControlMessage(message=MSPControlMessage.END_OF_FILE, source=self)
        else:
            return MSPDataFrame(**json.loads(s=line, cls=MSPDataFrame.JsonDecoder))

    def _stop(self):
        self._file_handle.close()
