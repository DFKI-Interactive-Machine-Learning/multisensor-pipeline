from abc import ABC
from typing import Optional
from time import time, sleep

from multisensor_pipeline.dataframe.control import MSPControlMessage
from multisensor_pipeline.dataframe.dataframe import MSPDataFrame
from multisensor_pipeline.modules.base.base import BaseSource


class BaseDatasetSource(BaseSource, ABC):
    """Base Module for DatasetSources."""

    def __init__(self, playback_speed: float = float("inf")):
        """
        Initialize the BaseDatasetSource.

        Args:
            playback_speed: sets the playback speed.
                            Default set to as fast as possible.
        """
        super(BaseDatasetSource, self).__init__()
        self._playback_speed = playback_speed
        self._last_frame_timestamp = None
        self._last_playback_timestamp = None

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
        Notify observers.

        If the frame is not null (End of Dataset) it notifies all observers
        that there's a new dataframe else it stops.

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
        Modify the dataframe timestamp corresponding the playback speed.

        Sleeps if necessary to achieve correct playback speed.

        Args:
            frame:  Dataframe
        """
        if isinstance(frame, MSPControlMessage):
            return
        if self._playback_speed == float("inf"):
            return

        if self._last_frame_timestamp is not None:
            original_delta = frame.timestamp - self._last_frame_timestamp
            target_delta = original_delta / self._playback_speed

            actual_delta = time() - self._last_playback_timestamp
            if actual_delta < target_delta:
                sleep(target_delta - actual_delta)

        self._last_frame_timestamp = frame.timestamp
        self._last_playback_timestamp = time()
        frame['playback_timestamp'] = self._last_playback_timestamp
