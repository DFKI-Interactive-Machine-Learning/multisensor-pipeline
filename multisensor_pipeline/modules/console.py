from . import BaseSink
from ..dataframe import MSPDataFrame


class ConsoleSink(BaseSink):

    def _update(self, frame: MSPDataFrame = None):
        if frame is not None:
            print(f"{frame.topic}:\t{frame}")
