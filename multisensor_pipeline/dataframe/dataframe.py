from typing import Any
import logging
from time import time
import json
import numpy as np

logger = logging.getLogger(__name__)


class Topic:

    def __init__(self, name: str, dtype: type = None, source_module: type = None):
        """

        :param name:
        :param dtype:
        :param source_module:
        """
        self._name = name
        self._dtype = dtype
        self._source = source_module

    @property
    def name(self) -> str:
        return self._name

    @property
    def dtype(self) -> type:
        return self._dtype

    @property
    def source_module(self) -> type:
        return self._source

    def __eq__(self, other):
        if not isinstance(other, Topic):
            return False
        return self.dtype == other.dtype and self.name == other.name and self.source_module == other.source_module

    def __str__(self):
        return f"{self.source_module.__name__}:{self.name}:{self.dtype.__name__}"


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
                        "source_module": str(obj.source_module)
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
                    # TODO: decode class types
            return obj

    def __init__(self, topic: Topic, value, timestamp: float = None, **kwargs):
        super(MSPDataFrame, self).__init__()
        if timestamp is None:
            self['timestamp'] = time()
        else:
            self['timestamp'] = timestamp
        self['topic'] = topic
        self['value'] = value

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
    def value(self):
        return self['value']

    @value.setter
    def value(self, value):
        self['value'] = value


class MSPEventFrame(MSPDataFrame):

    def __init__(self, duration: float = 0, label: str = None, value=None, **kwargs):
        super(MSPEventFrame, self).__init__(duration=duration, label=label, value=value, **kwargs)

    @property
    def duration(self) -> float:
        return self['duration']

    @duration.setter
    def duration(self, value: float):
        self['duration'] = value

    @property
    def label(self) -> str:
        return self['label']

    @label.setter
    def label(self, value: str):
        self['label'] = value
