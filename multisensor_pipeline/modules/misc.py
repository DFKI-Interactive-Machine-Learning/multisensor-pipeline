from multisensor_pipeline import BaseProcessor
from multisensor_pipeline.utils.dataframe import MSPDataFrame


class TimestampExtractionProcessor(BaseProcessor):

    def __init__(self, target_dtype=None):
        super(TimestampExtractionProcessor, self).__init__()
        self._target_dtype = target_dtype

    def _update_loop(self):
        while self._active:
            dtype, dataframe = self.get()
            if self._target_dtype is not None and dtype != self._target_dtype:
                continue

            assert isinstance(dataframe, MSPDataFrame)
            time_dataframe = MSPDataFrame(timestamp=dataframe.timestamp)
            self._notify_all(dtype=dtype, data=time_dataframe, suffix="timestamp")
