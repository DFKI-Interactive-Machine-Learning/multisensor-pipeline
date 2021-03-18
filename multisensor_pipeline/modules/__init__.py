from .base import BaseProcessor, BaseSink, BaseSource


class PassthroughProcessor(BaseProcessor):
    def _update(self, frame=None):
        self._notify(frame)
