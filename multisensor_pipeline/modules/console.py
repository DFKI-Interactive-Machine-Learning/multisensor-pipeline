from multisensor_pipeline.modules.base import BaseSink


class ConsoleSink(BaseSink):

    def _update(self, frame=None):
        if frame is not None:
            print(f"{frame.dtype}:\t{frame}")
