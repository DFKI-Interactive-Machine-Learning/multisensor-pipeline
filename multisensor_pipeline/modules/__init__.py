from .base import BaseProcessor, BaseSink, BaseSource
from queue import Queue

from ..dataframe import MSPDataFrame


class PassthroughProcessor(BaseProcessor):
    def _update(self, frame=None):
        self._notify(frame)


class ListSink(BaseSink):

    def __init__(self):
        super(ListSink, self).__init__()
        self._list = []

    @property
    def list(self):
        return self._list

    def _update(self, frame: MSPDataFrame = None):
        self._list.append(frame)


class QueueSink(BaseSink):

    def __init__(self):
        super(QueueSink, self).__init__()
        self._q = Queue()

    @property
    def queue(self):
        return self._q

    def _update(self, frame: MSPDataFrame = None):
        self._q.put(frame)

    def get(self):
        self._q.get()

    def empty(self):
        self._q.empty()


class ConsoleSink(BaseSink):

    def _update(self, frame: MSPDataFrame = None):
        if frame is not None:
            print(f"{frame.topic}:\t{frame}")


class TimestampExtractionProcessor(BaseProcessor):

    def __init__(self, target_topic_name=None):
        super(TimestampExtractionProcessor, self).__init__()
        self._topic_name = target_topic_name

    def _update(self, frame: MSPDataFrame = None):
        if self._topic_name is None and frame.topic.name == self._topic_name:
            _topic = self._generate_topic(name=f"{frame.topic.name}.timestamp")
            return MSPDataFrame(topic=_topic, timestamp=frame.timestamp)
