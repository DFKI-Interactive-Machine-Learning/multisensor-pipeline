from typing import Any, Optional, Dict, TypeVar, Generic
import logging
from time import time
import json
import numpy as np
from enum import Enum, unique

logger = logging.getLogger(__name__)
T = TypeVar('T')


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
        return f"{self.name}:{self.dtype if self.dtype is not None else None}"

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


class MSPDataFrame(Generic[T]):
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

    def __init__(self, topic: Topic, timestamp: float = None, duration: float = 0, data: Optional[T] = None):
        super(MSPDataFrame, self).__init__()
        self._timestamp = time() if timestamp is None else timestamp
        self._duration = duration
        self._topic = topic
        self._source_module = None
        self._data = data

    @property
    def timestamp(self) -> float:
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp: float):
        self._timestamp = timestamp

    @property
    def topic(self) -> Topic:
        return self._topic

    @topic.setter
    def topic(self, topic: Topic):
        self._topic = topic

    @property
    def source_module(self):
        return self._source_module

    @source_module.setter
    def source_module(self, source):
        self._source_module = source

    @property
    def data(self) -> T:
        return self._data

    @data.setter
    def data(self, data: T):
        self._data = data

    @property
    def duration(self) -> float:
        return self._duration

    @duration.setter
    def duration(self, duration: float):
        self._duration = duration

