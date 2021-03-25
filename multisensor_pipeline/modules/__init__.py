from .base import BaseProcessor, BaseSink, BaseSource
from queue import Queue

from ..dataframe import MSPDataFrame


class PassthroughProcessor(BaseProcessor):
    def _update(self, frame=None):
        self._notify(frame)


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


