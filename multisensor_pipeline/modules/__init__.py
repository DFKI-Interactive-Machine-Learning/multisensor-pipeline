from .base import BaseProcessor, BaseSink, BaseSource
from queue import Queue
from time import sleep
from ..dataframe import MSPDataFrame


class PassthroughProcessor(BaseProcessor):
    def on_update(self, frame=None):
        self._notify(frame)


class SleepPassthroughProcessor(BaseProcessor):

    def __init__(self, sleep_time, **kwargs):
        super().__init__(**kwargs)
        self._sleep_time = sleep_time

    def on_update(self, frame: MSPDataFrame = None):
        self._notify(frame)
        sleep(self._sleep_time)


class TimestampExtractionProcessor(BaseProcessor):

    def __init__(self, target_topic_name=None):
        super(TimestampExtractionProcessor, self).__init__()
        self._topic_name = target_topic_name

    def on_update(self, frame: MSPDataFrame = None):
        if self._topic_name is None and frame.topic.name == self._topic_name:
            _topic = self._generate_topic(name=f"{frame.topic.name}.timestamp")
            return MSPDataFrame(topic=_topic, timestamp=frame.timestamp)


class ListSink(BaseSink):

    def __init__(self):
        super(ListSink, self).__init__()
        self._list = []

    @property
    def list(self):
        return self._list

    def on_update(self, frame: MSPDataFrame = None):
        self._list.append(frame)


class QueueSink(BaseSink):

    def __init__(self):
        super(QueueSink, self).__init__()
        self._q = Queue()

    @property
    def queue(self):
        return self._q

    def on_update(self, frame: MSPDataFrame = None):
        self._q.put(frame)

    def get(self):
        self._q.get()

    def empty(self):
        self._q.empty()


class ConsoleSink(BaseSink):

    def on_update(self, frame: MSPDataFrame = None):
        if frame is not None:
            print(f"{frame.topic}:\t{frame}")


class TrashSink(BaseSink):

    def on_update(self, frame: MSPDataFrame = None):
        pass


class SleepTrashSink(TrashSink):

    def __init__(self, sleep_time: float, **kwargs):
        super().__init__(**kwargs)
        self._sleep_time = sleep_time

    def on_update(self, frame: MSPDataFrame = None):
        sleep(self._sleep_time)
