from abc import ABC
from typing import List
from multisensor_pipeline.modules.base import BaseSink
from multisensor_pipeline.dataframe import MSPDataFrame
from pathlib import Path
import json


class RecordingSink(BaseSink, ABC):

    @property
    def target(self) -> Path:
        return self._target

    @property
    def topics(self) -> List[str]:
        return self._topics

    @property
    def override(self) -> bool:
        return self._override

    def __init__(self, target, topics: List = None, override=False):
        super(RecordingSink, self).__init__()

        # set target path or file
        self._target = Path(target)
        if self._target.is_dir() and not self._target.exists():
            self._target.mkdir(parents=True, exist_ok=True)
        # set topic filter
        self._topics = topics
        # set override flag
        self._override = override

    def check_topic(self, topic):
        """Check whether the given topic shall be captured."""
        if self._topics is None:
            return True
        return any([t == topic for t in self._topics])

    def on_update(self, frame: MSPDataFrame = None):
        if self.check_topic(frame.topic):
            self.write(frame)

    def write(self, frame):
        raise NotImplementedError()


class JsonRecordingSink(RecordingSink):

    _json_file = None

    def on_start(self):
        assert self.target.suffix == ".json", f"The file extension must be json, but was {self.target.suffix}"
        if not self.override:
            assert not self.target.exists(), f"The file existis, but override is disabled ({self.target})"
        self._json_file = self.target.open(mode="w")

    def write(self, frame):
        self._json_file.write(json.dumps(obj=frame, cls=MSPDataFrame.JsonEncoder) + '\n')

    def on_stop(self):
        self._json_file.close()
