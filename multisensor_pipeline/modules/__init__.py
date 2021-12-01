from .base import BaseProcessor, BaseSink, BaseSource
from typing import Optional, List
from queue import Queue
from time import sleep
from ..dataframe import MSPDataFrame, Topic


class PassthroughProcessor(BaseProcessor):
    def on_update(self, frame: MSPDataFrame) -> Optional[MSPDataFrame]:
        return frame


class SleepPassthroughProcessor(BaseProcessor):

    def __init__(self, sleep_time, **kwargs):
        super().__init__(**kwargs)
        self._sleep_time = sleep_time

    def on_update(self, frame: MSPDataFrame) -> Optional[MSPDataFrame]:
        sleep(self._sleep_time)
        return frame


class AttributeExtractionProcessor(BaseProcessor):

    def __init__(self, target_topic_name=None, key="timestamp"):
        super(AttributeExtractionProcessor, self).__init__()
        self._topic_name = target_topic_name
        self._key = key

    def on_update(self, frame: MSPDataFrame) -> Optional[MSPDataFrame]:
        if (self._topic_name is None or frame.topic.name == self._topic_name) and self._key in frame:
            _topic = self._generate_topic(name=f"{frame.topic.name}.{self._key}")
            return MSPDataFrame(topic=_topic, timestamp=frame['key'])


class ListSink(BaseSink):

    def __init__(self):
        super(ListSink, self).__init__()
        self._list = []

    @property
    def list(self):
        return self._list

    def on_update(self, frame: MSPDataFrame):
        self._list.append(frame)

    def __len__(self):
        return len(self._list)


class QueueSink(BaseSink):

    def __init__(self):
        super(QueueSink, self).__init__()
        self._q = Queue()

    @property
    def queue(self):
        return self._q

    def on_update(self, frame: MSPDataFrame):
        self._q.put(frame)

    def get(self):
        self._q.get()

    def empty(self):
        self._q.empty()


class ConsoleSink(BaseSink):
    """ Prints incoming frames to the console. """

    def on_update(self, frame: MSPDataFrame):
        if frame is not None:
            print(f"{frame.topic}:\t{frame}")


class TrashSink(BaseSink):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._counter = 0

    def on_update(self, frame: MSPDataFrame):
        self._counter += 1

    @property
    def counter(self) -> int:
        return self._counter


class SleepTrashSink(TrashSink):

    def __init__(self, sleep_time: float, **kwargs):
        super().__init__(**kwargs)
        self._sleep_time = sleep_time

    def on_update(self, frame: MSPDataFrame):
        sleep(self._sleep_time)
        self._counter += 1

    @property
    def counter(self) -> int:
        return self._counter
