from multisensor_pipeline.modules.base import BaseSink


class ConsoleSink(BaseSink):

    def _update_loop(self):
        while self._active:
            dtype, data = self.get()
            print(f"{dtype}:\t{data}")
