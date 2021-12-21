from abc import ABC
import logging
from multisensor_pipeline.modules import BaseSource
import time
import sched

logger = logging.getLogger(__name__)


class BaseDiscreteSamplingSource(BaseSource, ABC):

    def __init__(self, samplerate: float = 1.):
        """
        Args:
            samplerate: set the intended samplerate in Hertz [Hz]
        """
        super().__init__()
        self._samplerate = samplerate
        self._period_time = 1. / self._samplerate

        self._scheduler = sched.scheduler(time.perf_counter, time.sleep)

    @property
    def samplerate(self):
        return self._samplerate

    def _worker(self):
        t = time.perf_counter()
        self._notify(self.on_update())
        while self._active:
            t_next = t + self._period_time
            _ = self._scheduler.enterabs(
                time=t_next,
                priority=0,
                action=lambda: self._notify(self.on_update())
            )
            t = t_next
            self._scheduler.run(blocking=True)
