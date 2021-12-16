from abc import ABC
from multisensor_pipeline.dataframe import MSPDataFrame
from multisensor_pipeline.modules import BaseSource
from typing import Optional
import time
import sched


class BaseDatasetSource(BaseSource, ABC):
    """
    Base Module for DatasetSources
    """
    def __init__(self, playback_speed: float = float("inf")):
        """
        Initializes the BaseDatasetSource
        Args:
            playback_speed: sets the playback speed (1 is original playback speed). Default set to as fast as possible.
        """
        super(BaseDatasetSource, self).__init__()
        self._playback_speed = playback_speed
        self._last_frame_timestamp = None
        self._last_playback_timestamp = None
        if not self._playback_speed == float("inf"):
            self._scheduler = sched.scheduler(time.perf_counter, time.sleep)

    @property
    def eof(self):
        return not self.active

    @property
    def playback_speed(self):
        return self._playback_speed

    def _auto_stop(self):
        self.stop(blocking=False)

    def _notify(self, frame: Optional[MSPDataFrame]):
        """
        If the frame is not null (End of Dataset) it notifies all observers that there's a new dataframe else it stops
        Args:
            frame:  Dataframe
        """
        if frame is None:
            self._auto_stop()
        else:
            self._sleep(frame)
            super(BaseDatasetSource, self)._notify(frame)

    def _sleep(self, frame: MSPDataFrame):
        """
        Modifies the dataframe timestamp corresponding the playback speed.
        Sleeps if necessary to achieve correct playback speed
        Args:
            frame:  Dataframe
        """
        if self._playback_speed == float("inf"):
            return
        if frame.topic.is_control_topic:
            return

        if self._last_frame_timestamp is not None:
            original_delta = frame.timestamp - self._last_frame_timestamp
            target_delta = original_delta / self._playback_speed

            actual_delta = time.perf_counter() - self._last_playback_timestamp
            if actual_delta < target_delta:
                time.sleep(target_delta - actual_delta)

        self._last_frame_timestamp = frame.timestamp
        self._last_playback_timestamp = time.perf_counter()
        # TODO: set replay timestamp -> was used to check timing in "test recording and replay"

