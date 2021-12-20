from multisensor_pipeline.dataframe import MSPDataFrame
from multisensor_pipeline.modules.persistence.dataset import BaseDatasetSource
from typing import Optional
from pathlib import Path


class DefaultReplaySource(BaseDatasetSource):
    """
    The DefaultReplaySource loads a recorded dataset (from the DefaultRecordingSink) and replays it:
    it simulates the recorded stream by sending all dataframes in the same order into a connected pipeline.
    """

    def __init__(self, file_path: str, **kwargs):
        """
        Initializes the source
        Args:
            file_path: file path to the recording
        """
        super(DefaultReplaySource, self).__init__(**kwargs)
        self._file_path = Path(file_path)
        self._file_handle = None
        self._unpacker = None

        assert self._file_path.exists() and self._file_path.is_file()
        assert self._file_path.suffix == ".msgpack"

    def on_start(self):
        self._file_handle = open(self._file_path, mode="rb")
        self._unpacker = MSPDataFrame.get_msgpack_unpacker(self._file_handle)

    def on_update(self) -> Optional[MSPDataFrame]:
        """
        Iterates over the entries in the recorded file and returns all dataframes. Stops if EOF is reached
        """
        try:
            frame = next(self._unpacker)
        except StopIteration:
            frame = None

        if frame is not None:
            return frame
        else:
            # EOF is reached -> auto-stop (you can alternatively return None)
            self._auto_stop()

    def on_stop(self):
        self._file_handle.close()
