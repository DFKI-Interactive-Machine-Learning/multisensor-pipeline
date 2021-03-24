from abc import ABC
import json
from multisensor_pipeline.dataframe import MSPDataFrame
from multisensor_pipeline.modules import BaseSource


class BaseDatasetSource(BaseSource, ABC):
    pass


class JsonDatasetSource(BaseDatasetSource):

    def __init__(self, file_path):
        super(JsonDatasetSource, self).__init__()
        self._file_path = file_path
        self._file_handle = None

    def _start(self):
        self._file_handle = open(self._file_path, mode="r")

    def _update(self) -> MSPDataFrame:
        # TODO: check if EOF is reached -> auto-close
        line = next(self._file_handle)
        dict = json.loads(s=line, cls=MSPDataFrame.JsonDecoder)
        frame = MSPDataFrame(**dict)
        return frame

    def _stop(self):
        self._file_handle.close()
