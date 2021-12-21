from abc import ABC
from typing import List, Optional
from multisensor_pipeline.modules.base import BaseSink
from multisensor_pipeline.dataframe import MSPDataFrame, Topic
from pathlib import Path


class RecordingSink(BaseSink, ABC):
    """
    RecordingSink replays a recorded json dataset
    """

    @property
    def target(self) -> Path:
        return self._target

    @property
    def topics(self) -> Optional[List[Topic]]:
        return self._topics

    @property
    def override(self) -> bool:
        return self._override

    def __init__(self, target, topics: Optional[List[Topic]] = None, override=False):
        """
        initializes RecordingSink
        Args:
            target: filepath
            topics: Filter which topics should be recorded
            override: Flag to set overwrite rules
        """
        super(RecordingSink, self).__init__()

        # set target path or file
        self._target = Path(target)
        if self._target.is_dir() and not self._target.exists():
            self._target.mkdir(parents=True, exist_ok=True)
        # set topic filter
        self._topics = topics
        # set override flag
        self._override = override

    def check_topic(self, topic: Topic):
        """Check whether the given topic shall be captured."""
        if self._topics is None:
            return True
        return any([t == topic for t in self._topics])

    def on_update(self, frame: MSPDataFrame):
        if self.check_topic(frame.topic):
            self.write(frame)

    def write(self, frame):
        """ Custom write routine. """
        raise NotImplementedError()


class DefaultRecordingSink(RecordingSink):
    """
    The DefaultRecordingSink enables recording of dataframes for all connected modules and topics.
    It uses the default serialization based on msgpack.
    """

    _file_handle = None

    def on_start(self):
        assert self.target.suffix == ".msgpack", f"The file extension must be json, but was {self.target.suffix}"
        if not self.override:
            assert not self.target.exists(), f"The file existis, but override is disabled ({self.target})"

        self._file_handle = self.target.open(mode="wb")

    def write(self, frame):
        self._file_handle.write(frame.serialize())

    def on_stop(self):
        self._file_handle.close()
