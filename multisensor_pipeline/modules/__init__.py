from multisensor_pipeline.modules.base import BaseProcessor


class PassthroughProcessor(BaseProcessor):

    def _update(self):
        while self._active:
            event, data = self.get()
            self._notify_all(event, data)