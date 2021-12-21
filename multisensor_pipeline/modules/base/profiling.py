import logging
from typing import Optional
from multisensor_pipeline.dataframe import MSPDataFrame, MSPControlMessage, Topic
from datetime import datetime
from collections import deque
import time


class MSPModuleStats:
    """
    Profiling of the pipeline
    """
    class MovingAverageStats(object):
        """
          Implementation of MovingAverageStats see https://en.wikipedia.org/wiki/Moving_average
        """

        def __init__(self, k=20):
            self._k = k  # window size for moving average
            self._samples = deque(maxlen=k)
            self._num_samples = 0  # number of received frames
            self._sma = 0  # simple moving average
            self._cma = 0  # cumulative moving average

        def _next_sma(self, rate: float):
            # see https://en.wikipedia.org/wiki/Moving_average
            self._samples.append(rate)
            if self._num_samples >= self._k - 1:
                return self._sma + (rate - self._samples.popleft()) / self._k
            else:
                return self._cma

        def _next_cma(self, rate: float):
            # see https://en.wikipedia.org/wiki/Moving_average
            return (rate + self._num_samples * self._cma) / (self._num_samples + 1)

        def update(self, sample: float):
            self._cma = self._next_cma(sample)
            self._sma = self._next_sma(sample)
            self._num_samples += 1

        @property
        def sma(self):
            return self._sma

        @property
        def cma(self):
            return self._cma

    class RobustSamplerateStats(object):

        def __init__(self, max_measurement_interval: float = 1. / 10):
            super(MSPModuleStats.RobustSamplerateStats, self).__init__()
            self._num_samples = 0
            self._samplerate = 0.
            self._t_start = None
            self._t_last_update = None
            self._measurement_interval = max_measurement_interval

        def update(self, timestamp: float):
            if self._t_start is None:
                self._t_start = timestamp
                self._t_last_update = timestamp
            self._num_samples += 1

            time_since_last_update = timestamp - self._t_last_update
            if time_since_last_update >= self._measurement_interval:
                measurement_time = timestamp - self._t_start
                self._samplerate = float(self._num_samples - 1.) / measurement_time
                self._t_last_update = timestamp

        @property
        def samplerate(self):
            return self._samplerate

    class Direction:
        OUT = 0
        IN = 1

    def __init__(self):
        """
            Initialize the Profiling of the pipeline
        """
        self._start_time = datetime.now()
        self._stop_time = None

        self._in_stats = {}
        self._out_stats = {}
        self._queue_size = self.MovingAverageStats()
        self._skipped_frames = self.RobustSamplerateStats()

    def get_stats(self, direction: Direction, topic: Optional[Topic] = None):
        if direction == self.Direction.IN:
            if topic:
                return self._in_stats[topic.uuid]
            else:
                return self._in_stats
        elif direction == self.Direction.OUT:
            if topic:
                return self._out_stats[topic.uuid]
            return self._out_stats
        else:
            raise NotImplementedError()

    def add_frame(self, frame: MSPDataFrame, direction: Direction):
        time_received = time.perf_counter()
        if frame.topic.is_control_topic:
            return

        # per direction, topic -> update stats
        stats = self.get_stats(direction)
        if frame.topic.uuid not in stats:
            stats[frame.topic.uuid] = self.RobustSamplerateStats()
        stats[frame.topic.uuid].update(time_received)

    def add_queue_state(self, qsize: int, skipped_frames: int):
        time_received = time.perf_counter()
        self._queue_size.update(qsize)
        for i in range(skipped_frames):
            self._skipped_frames.update(time_received)

    @property
    def frame_skip_rate(self):
        return self._skipped_frames.samplerate

    @property
    def average_queue_size(self):
        return self._queue_size.cma

    def finalize(self):
        self._stop_time = datetime.now()
