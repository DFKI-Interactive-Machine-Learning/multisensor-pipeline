import json
from multisensor_pipeline.dataframe import MSPDataFrame
from multisensor_pipeline.modules.persistence.dataset import BaseDatasetSource
from typing import Optional


class JsonReplaySource(BaseDatasetSource):

    def __init__(self, file_path, **kwargs):
        super(JsonReplaySource, self).__init__(**kwargs)
        self._file_path = file_path
        self._file_handle = None

    def on_start(self):
        self._file_handle = open(self._file_path, mode="r")

    def on_update(self) -> Optional[MSPDataFrame]:
        line = self._file_handle.readline()
        if line != '':
            return MSPDataFrame(**json.loads(s=line, cls=MSPDataFrame.JsonDecoder))

        # EOF is reached -> auto-stop (you can alternatively return None)
        self._auto_stop()

    def on_stop(self):
        self._file_handle.close()
