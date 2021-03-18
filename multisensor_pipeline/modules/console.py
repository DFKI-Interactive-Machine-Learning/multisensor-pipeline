from multisensor_pipeline.modules.base import BaseSink, MSPDataFrame


class ConsoleSink(BaseSink):

    def _update(self, frame: MSPDataFrame = None):
        if frame is not None:
            print(f"{frame.topic}:\t{frame}")
