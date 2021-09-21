from typing import Any, Optional
import logging
from time import time
import json
import numpy as np
from enum import Enum, unique

logger = logging.getLogger(__name__)


class Topic:

    def __init__(self, name: Optional[str] = None, dtype: Optional[type] = None):
        """
        :param name:
        :param dtype:
        """
        self._name = name
        self._dtype = dtype

    @property
    def name(self) -> str:
        return self._name

    @property
    def dtype(self) -> type:
        return self._dtype

    @property
    def uuid(self):
        return f"{self.name}:{self.dtype.__name__ if self.dtype is not None else None}"

    def __hash__(self):
        return hash(self.uuid)

    def __eq__(self, other):
        if not isinstance(other, Topic):
            return False

        if other.dtype is not None:
            dtype_matches = other.dtype == self.dtype
        else:
            dtype_matches = True

        if other.name is not None:
            name_matches = other.name == self.name
        else:
            name_matches = True

        return dtype_matches and name_matches

    def __str__(self):
        return f"{self.dtype.__name__ if self.dtype is not None else None}:{self.name}"

    def __repr__(self):
        return f"Topic(dtype={self.dtype}, name={self.name})"


@unique
class TopicEnum(Enum):
    pass


class MSPDataFrame(dict):
    class JsonEncoder(json.JSONEncoder):

        def default(self, obj: Any) -> Any:
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return {
                    "_kind_": "ndarray",
                    "_value_": obj.tolist()
                }
            if isinstance(obj, Topic):
                assert isinstance(obj, Topic)
                return {
                    "_kind_": "topic",
                    "_value_": {
                        "name": obj.name,
                        "dtype": str(obj.dtype)
                    }
                }
            return super(MSPDataFrame.JsonEncoder, self).default(obj)

    class JsonDecoder(json.JSONDecoder):

        def __init__(self, *args, **kwargs):
            json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

        def object_hook(self, obj):
            if '_kind_' in obj:
                kind = obj['_kind_']
                if kind == 'ndarray':
                    return np.array(obj['_value_'])
                elif kind == 'topic':
                    return Topic(**obj['_value_'])
                    # TODO: decode class types (#22)
            return obj

    def __init__(self, topic: Topic, timestamp: float = None, **kwargs):
        super(MSPDataFrame, self).__init__()
        if timestamp is None:
            self['timestamp'] = time()
        else:
            self['timestamp'] = timestamp
        self['topic'] = topic

        self._source_module = None

        if kwargs is not None:
            self.update(kwargs)

    @property
    def timestamp(self) -> float:
        return self['timestamp']

    @timestamp.setter
    def timestamp(self, value: float):
        self['timestamp'] = value

    @property
    def topic(self) -> Topic:
        return self['topic']

    @topic.setter
    def topic(self, value: Topic):
        self['topic'] = value

    @property
    def source_module(self):
        return self._source_module

    @source_module.setter
    def source_module(self, value):
        self._source_module = value


class MSPEventFrame(MSPDataFrame):

    def __init__(self, value=None, duration: float = 0, **kwargs):
        super(MSPEventFrame, self).__init__(value=value, duration=duration, **kwargs)

    @property
    def duration(self) -> float:
        return self['duration']

    @duration.setter
    def duration(self, value: float):
        self['duration'] = value

    @property
    def value(self) -> str:
        return self['value']

    @value.setter
    def value(self, value: str):
        self['value'] = value
