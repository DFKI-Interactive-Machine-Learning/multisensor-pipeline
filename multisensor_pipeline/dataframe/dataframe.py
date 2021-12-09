from typing import Any, Optional, TypeVar, Generic
import logging
import io
from time import time
import msgpack
import numpy as np
from PIL import Image

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
        return f"{self.dtype if self.dtype is not None else None}:{self.name}"

    def __repr__(self):
        return f"Topic(dtype={self.dtype if self.dtype is not None else None}, name={self.name})"


class MSPDataFrame(Generic[T]):

    def __init__(self, topic: Topic, timestamp: float = None, duration: float = 0, data: Optional[T] = None):
        super(MSPDataFrame, self).__init__()
        self._timestamp = time() if timestamp is None else timestamp
        self._duration = duration
        self._topic = topic
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

    @staticmethod
    def msgpack_encode(obj):
        if isinstance(obj, MSPDataFrame):
            return {
                "__dataframe__": True,
                "topic": obj.topic,
                "timestamp": obj.timestamp,
                "duration": obj.duration,
                "data": obj.data
            }
        if isinstance(obj, Topic):
            return {
                "__topic__": True,
                "name": obj.name,
                "dtype": str(obj.dtype) if obj.dtype is not None else None  # TODO: how to encode a type?
            }
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return {
                "__ndarray__": True,
                "data": obj.tolist(),
                "shape": obj.shape,
                "dtype": obj.dtype.name
            }
        if isinstance(obj, Image.Image):
            buffer = io.BytesIO()
            obj.save(buffer, format="jpeg", quality=90)
            return {
                "__jpeg__": True,
                "bytes": buffer.getvalue()
            }
        return obj

    def serialize(self) -> bytes:
        return msgpack.packb(self, default=MSPDataFrame.msgpack_encode)

    @staticmethod
    def deserialize(frame: bytes):
        return msgpack.unpackb(frame, object_hook=MSPDataFrame.msgpack_decode, raw=False)

    @staticmethod
    def msgpack_decode(obj):
        if '__dataframe__' in obj:
            obj = MSPDataFrame(
                topic=obj["topic"],
                timestamp=obj["timestamp"],
                duration=obj["duration"],
                data=obj["data"]
            )
        elif '__topic__' in obj:
            obj = Topic(name=obj["name"], dtype=obj["dtype"])
        elif '__ndarray__' in obj:
            obj = np.array(
                object=obj["data"],
                # shape=obj["shape"],
                dtype=obj["dtype"]
            )
        elif '__jpeg__' in obj:
            obj = Image.open(io.BytesIO(obj["bytes"]))
        return obj

    @staticmethod
    def get_msgpack_unpacker(filehandle) -> msgpack.Unpacker:
        return msgpack.Unpacker(file_like=filehandle, object_hook=MSPDataFrame.msgpack_decode, raw=False)
