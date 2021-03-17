from abc import ABC
from typing import List
from .modules.base import BaseSink
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
        self._topics = [t if isinstance(t, str) else t.decode() for t in topics]
        # set override flag
        self._override = override

    def check_topic(self, topic):
        """Check whether the given topic shall be captured."""
        if self._topics is None:
            return True
        if isinstance(topic, bytes):
            topic = topic.decode()
        return any([topic.startswith(t) for t in self._topics])

    def _update_loop(self):
        while self._active:
            dtype, dataframe = self.get()
            if self.check_topic(dtype):
                self.write(dtype, dataframe)

    def write(self, topic, dataframe):
        raise NotImplementedError()


class JsonRecordingSink(RecordingSink):

    _json_file = None

    def _start(self):
        assert self.target.is_file(), f"The target must be a filepath, but was {self.target}"
        assert self.target.suffix == ".json", f"The file extension must be json, but was {self.target.suffix}"
        if not self.override:
            assert not self.target.exists(), f"The file existis, but override is disabled ({self.target})"
        self._json_file = self.target.open(mode="w")

    def write(self, topic, dataframe):
        d = {
            "dtype": str(topic),
            "dataframe": dataframe
        }
        self._json_file.write(json.dumps(d) + '\n')

    def _stop(self):
        self._json_file.close()
