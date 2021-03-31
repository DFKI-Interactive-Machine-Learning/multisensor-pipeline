from multisensor_pipeline.dataframe import MSPDataFrame, MSPControlMessage
from time import time
from datetime import datetime
from collections import deque


class MSPModuleStats:

    class MovingAverageStats(object):

        def __init__(self, k=20):
            self._k = k  # window size for moving average
            self._samples = deque(maxlen=k)
            self._num_samples = 0  # number of received frames
            self._sma = 0  # simple moving average
            self._cma = 0  # cumulative moving average

        def _next_sma(self, rate: float):
            # see https://en.wikipedia.org/wiki/Moving_average
            if self._num_samples >= self._k:
                return self._sma + (rate - self._samples.popleft()) / self._k
            else:
                self._samples.append(rate)
                return self._cma

        def _next_cma(self, rate: float):
            # see https://en.wikipedia.org/wiki/Moving_average
            return (rate + self._num_samples * self._cma) / (self._num_samples + 1)

        def update(self, sample: float):
            self._cma = self._next_cma(sample)
            self._sma = self._next_sma(sample)
            self._num_samples += 1

    class FrequencyStats(MovingAverageStats):

        _last_sample = None  # timestamp of last frame (time of being received)

        def update(self, sample: float):
            if self._last_sample is not None:
                rate = 1. / (sample - self._last_sample)
                super(MSPModuleStats.FrequencyStats, self).update(rate)
            self._last_sample = sample

    class Direction:
        OUT = 0
        IN = 1

    def __init__(self):
        self._start_time = datetime.now()
        self._stop_time = None

        self._in_stats = {}
        self._out_stats = {}
        self._queue_size = self.MovingAverageStats()
        self._skipped_frames = self.MovingAverageStats()

    def get_stats(self, direction: Direction):
        if direction == self.Direction.IN:
            return self._in_stats
        elif direction == self.Direction.OUT:
            return self._out_stats
        else:
            raise NotImplementedError()

    def add_frame(self, frame: MSPDataFrame, direction: Direction):
        time_received = time()
        if isinstance(frame, MSPControlMessage):
            return

        # per direction, topic -> update stats
        stats = self.get_stats(direction)
        if frame.topic not in stats:
            stats[frame.topic] = self.FrequencyStats()
        stats[frame.topic].update(time_received)

    def add_queue_state(self, qsize: int, skipped_frames: int):
        self._queue_size.update(qsize)
        self._skipped_frames.update(skipped_frames)

    def finalize(self):
        self._stop_time = datetime.now()
