from typing import Optional, TypeVar, Generic, Any
import logging
import io
import time
import msgpack
import numpy as np

from PIL import Image

logger = logging.getLogger(__name__)
T = TypeVar('T')


class Topic:

    def __init__(self, dtype: type = Any, name: Optional[str] = None,):
        """
        :param name:
        :param dtype:
        """
        self._name = name
        self._dtype = dtype
        if self.name is not None and dtype == Any:
            logger.warning("If dtype is Any, topic.name has no effect.")

    @property
    def name(self) -> str:
        return self._name

    @property
    def dtype(self) -> type:
        return self._dtype

    @property
    def uuid(self):
        return f"{self.name}:{self.dtype if self.dtype is not None else None}"

    @property
    def is_control_topic(self):
        return self.dtype == MSPControlMessage.ControlTopic.ControlType

    def __hash__(self):
        return hash(self.uuid)

    def __eq__(self, sink_topic):
        """
        Args:
            sink_topic: Sink
            TODO:
        Returns:
        """
        if not isinstance(sink_topic, Topic):
            return False    #TODO: can we replace isinstance?

        if self.dtype is Any or sink_topic.dtype is Any:
            return True

        dtype_matches = sink_topic.dtype == self.dtype

        if sink_topic.name is not None:
            name_matches = sink_topic.name == self.name
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
        self._timestamp = time.perf_counter() if timestamp is None else timestamp
        self._duration = duration
        self._topic = topic
        self._data = data
        self._source_uuid = None

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
    def source_uuid(self) -> str:
        return self._source_uuid

    @source_uuid.setter
    def source_uuid(self, source_uuid: str):
        self._source_uuid = source_uuid

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
        if isinstance(obj, np.float):
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


class MSPControlMessage(MSPDataFrame):

    class ControlTopic(Topic):
        class ControlType:
            pass
        name = None
        dtype = ControlType

    END_OF_STREAM = "EOS"
    PASS = "PASS"

    def __init__(self, message):
        topic = self.ControlTopic()
        super(MSPControlMessage, self).__init__(topic=topic)
        self._data = message