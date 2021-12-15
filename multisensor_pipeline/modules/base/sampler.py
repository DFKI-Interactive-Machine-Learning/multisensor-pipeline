from abc import ABC
import logging
from multisensor_pipeline.modules import BaseSource
from multisensor_pipeline.dataframe import MSPDataFrame, MSPControlMessage
from time import time, sleep

logger = logging.getLogger(__name__)


class BaseFixedRateSource(BaseSource, ABC):

    def __init__(self, samplerate: float = 1.):
        """
        Args:
            samplerate: set the intended samplerate in Hertz [Hz]
        """
        super().__init__()
        self._samplerate = samplerate
        self._sleep_time = 1. / self._samplerate

        self._t_last = None

    @property
    def sampling_rate(self):
        return self._samplerate

    def _notify(self, frame: MSPDataFrame):
        super(BaseFixedRateSource, self)._notify(frame)
        self._sleep(frame)

    def _sleep(self, frame: MSPDataFrame):
        if self._samplerate == float("inf"):
            return
        if frame.topic.is_control_topic:
            return

        # ignore processing time for the first frame, as we cannot compute it
        if self._t_last is None:
            sleep(self._sleep_time)
        # this is any frame after the first one
        else:
            t_now = time()
            t_processing = t_now - self._t_last

             # Default case: processing time takes a small portion of the required sleep time -> compensate for this
            if t_processing < self._sleep_time:
                sleep(self._sleep_time - t_processing)
            # In any other case, i.e., t_processing >= self._sleep_time, we don't sleep.
            # If the processing time is larger than the sleep time, the source will fail to deliver its samples on time
            elif t_processing > self._sleep_time:
                logger.warning(f"The processing time of {self.name} takes longer than required for the defined "
                               f"samplerate of {self._samplerate} Hz. Processing takes {t_processing} s.")

        # after this statement, the processing time for preparing the next frame begins
        self._t_last = time()


if __name__ == '__main__':
    from multisensor_pipeline.pipeline import GraphPipeline
    from multisensor_pipeline.modules import BaseSink
    from multisensor_pipeline.modules.npy import RandomArraySource
    import numpy as np

    class TimestampListSink(BaseSink):

        def __init__(self):
            super(TimestampListSink, self).__init__()
            self.timestamps = []

        def on_update(self, frame: MSPDataFrame):
            self.timestamps.append(frame.timestamp)

    def _run_test_pipeline(samplerate: int, shape):
        # define the modules
        source = RandomArraySource(
            shape=shape,
            samplerate=samplerate,
            max_count=samplerate
        )
        sink = TimestampListSink()

        # add module to a pipeline...
        pipeline = GraphPipeline()
        pipeline.add(modules=[source, sink])
        # ...and connect the modules
        pipeline.connect(module=source, successor=sink)

        pipeline.start()
        sleep(1.05)
        pipeline.stop()
        pipeline.join()

        return np.array(sink.timestamps)

    # test timings for increasing number of array sizes and increasing samplerates
    print("starting load test for fixed rate source...")
    for shape in [None]:  # , (100,), (100, 100, 100), (1000, 1000, 1000)
        for samplerate in [1000]: # 10, 100,
            timestamps = _run_test_pipeline(samplerate=samplerate, shape=shape)
            n = len(timestamps)
            frametimes = np.diff(timestamps)
            mean, sd, t_min, t_max = frametimes.mean(), frametimes.std(), frametimes.min(), frametimes.max()

            print(f"shape={shape}, rate={samplerate}, n_rec={n}, t_mean={mean} (SD={sd}, range=[{t_min};{t_max}])")
            pass
            # TODO: asserts


