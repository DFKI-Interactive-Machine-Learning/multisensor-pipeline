from typing import Any
import logging
from time import time
import json
import numpy as np

logger = logging.getLogger(__name__)


class Topic:

    def __init__(self, name: str = "Any", dtype: type = None):
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
        return f"{self.name}:{self.dtype.__name__}"

    def __hash__(self):
        return hash(self.uuid)

    def __eq__(self, other):
        if not isinstance(other, Topic):
            return False
        if other.name == "Any":
            if other.dtype:
                return other.dtype == self.dtype
            else:
                True
        elif other.name == self._name:
            if other.dtype:
                return other.dtype == self._dtype
            else:
                True

    def __str__(self):
        return f"{self.name}:{self.dtype.__name__}"

    def __repr__(self):
        return f"Topic(name={self.name}, dtype={self.dtype})"


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
                        "dtype": str(obj.dtype),
                        "source_module": str(obj.source_module),
                        "source_uuid": obj.source_uuid
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
