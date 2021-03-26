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
