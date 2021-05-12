import json
from typing import Optional

from multisensor_pipeline.dataframe.dataframe import MSPDataFrame
from multisensor_pipeline.modules.persistence.dataset import BaseDatasetSource


class JsonReplaySource(BaseDatasetSource):
    """JsonReplaySource replays a recorded json dataset."""

    def __init__(self, file_path: str, **kwargs):
        """
        Initialize the source.

        Args:
            file_path: file path to the json file
        """
        super(JsonReplaySource, self).__init__(**kwargs)
        self._file_path = file_path
        self._file_handle = None

    def on_start(self):
        self._file_handle = open(self._file_path, mode="r")

    def on_update(self) -> Optional[MSPDataFrame]:
        """
        Iterate over the entries in the json file and returns a dataframe.

        Stops, if EOF is reached.
        """
        line = self._file_handle.readline()
        if line != '':
            return MSPDataFrame(
                **json.loads(s=line, cls=MSPDataFrame.JsonDecoder)
            )

        # EOF is reached -> auto-stop (you can alternatively return None)
        self._auto_stop()

    def on_stop(self):
        """Stop and cleanup."""
        self._file_handle.close()
