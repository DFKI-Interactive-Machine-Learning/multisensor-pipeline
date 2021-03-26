from abc import ABC
import json
from multisensor_pipeline.dataframe import MSPDataFrame, Topic
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
        line = self._file_handle.readline()
        if line == '':
            # EOF is reached -> auto-stop
            self.stop(blocking=False)
            return MSPDataFrame(topic=self._generate_topic("none"), value=None)
        else:
            return MSPDataFrame(**json.loads(s=line, cls=MSPDataFrame.JsonDecoder))

    def _stop(self):
        self._file_handle.close()