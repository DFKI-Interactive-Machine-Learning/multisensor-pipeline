from abc import ABC
from multisensor_pipeline.dataframe import MSPControlMessage
from multisensor_pipeline.modules import BaseSource


class BaseDatasetSource(BaseSource, ABC):

    def __init__(self):
        super(BaseDatasetSource, self).__init__()

    @property
    def eof_message(self):
        return MSPControlMessage(message=MSPControlMessage.END_OF_FILE, source=self)

    def _worker(self):
        while self._active:
            frame = self._update()
            if isinstance(frame, MSPControlMessage) and frame.message == MSPControlMessage.END_OF_FILE:
                self.stop(blocking=False)
                continue
            self._notify(frame)
