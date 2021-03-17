from typing import List, Dict
import logging
from time import time
from queue import Queue

logger = logging.getLogger(__name__)


class MSPDataFrame(dict):

    def _set_attr_from_value_or_dict(self, key, value, init_dict=None):
        self[key] = value
        if init_dict is not None:
            for k in [key, key.encode()]:
                if k in init_dict:
                    self[key] = init_dict[k]
                    del (init_dict[k])

    def __init__(self, dtype=None, init_dict: dict = None, timestamp: float = None):
        super(MSPDataFrame, self).__init__()
        if timestamp is None:
            self['timestamp'] = time()
        else:
            self['timestamp'] = timestamp
        # if type(dtype) is not bytes:
        #     dtype = str(dtype).encode()
        self['dtype'] = dtype
        assert dtype is not None

        self._set_attr_from_value_or_dict(key='dtype', value=self['dtype'], init_dict=init_dict)
        self._set_attr_from_value_or_dict(key='timestamp', value=self['timestamp'], init_dict=init_dict)
        if init_dict is not None:
            self.update(init_dict)

    @property
    def timestamp(self):
        return self['timestamp']

    @timestamp.setter
    def timestamp(self, value):
        self['timestamp'] = value

    @property
    def dtype(self):
        return self['dtype']

    @dtype.setter
    def dtype(self, value):
        self['dtype'] = value


class MSPEventFrame(MSPDataFrame):

    def __init__(self, duration=0, label=None, **kwargs):
        self._set_attr_from_value_or_dict('duration', duration, kwargs['init_dict'] if 'init_dict' in kwargs else None)
        self._set_attr_from_value_or_dict('label', label, kwargs['init_dict'] if 'init_dict' in kwargs else None)
        super(MSPEventFrame, self).__init__(**kwargs)

    @property
    def duration(self):
        return self['duration']

    @duration.setter
    def duration(self, value):
        self['duration'] = value

    @property
    def label(self):
        return self['label']

    @label.setter
    def label(self, value):
        self['label'] = value


class TypeInfo:

    def __init__(self, dtype: type, name: str, source: str = "generic", **kwargs):
        self._name = name
        self._dtype = dtype
        self._attributes = kwargs
        self._source = source

    @property
    def name(self):
        return self._name

    @property
    def dtype(self):
        return self._dtype

    @property
    def source(self):
        return self._source

    def attribute(self, key):
        if key in self._attributes:
            return self._attributes[key]
        return None

    def matches(self, type_infos: List):
        """Checks whether there's a match in a list of TypeInfo instances."""
        return any([self == t for t in type_infos])

    @staticmethod
    def multi_match(source, sink):
        """
        Checks whether there's a match between two lists of TypeInfo instances.
        Returns True, if any combination was a match, or if any type info was None (backwards compatibility).
        """
        if isinstance(sink, Queue):
            logger.warning(f"Sink has type Queue which is not recommended.")
            return True
        if source.offers is None or sink.consumes is None:
            offer_str = "generic" if source.offers is None else [str(t) for t in source.offers]
            consume_str = "generic" if sink.consumes is None else [str(t) for t in sink.consumes]
            logger.debug(f"Typing is not complete: offers {offer_str}; consumes {consume_str}.")
            return True
        return any([t.matches(sink.consumes) for t in source.offers])

    def __eq__(self, other):
        return self.dtype == other.dtype

    def __str__(self):
        return f"{self._source}.{self.name}.{self.dtype.__name__}"


# class CompoundType:
#
#     def __init__(self, timestamp=None):
#         if timestamp is None:
#             self._timestamp = time()
#         else:
#             self._timestamp = timestamp
#
#     @property
#     def timestamp(self):
#         return self._timestamp
#
#     @timestamp.setter
#     def timestamp(self, value):
#         self._timestamp = value


class TypeMismatchException(Exception):
    """Raised when a match of TypeInfos is required, but none was found."""

    def __init__(self, source, sink):
        self.source = source
        self.sink = sink
