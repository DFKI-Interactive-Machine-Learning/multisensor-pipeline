from abc import ABC
from typing import Optional, List

import av
from PIL import Image

from multisensor_pipeline.dataframe import Topic, MSPDataFrame
from multisensor_pipeline.modules.persistence import BaseDatasetSource


class PyAVSource(BaseDatasetSource, ABC):

    def __init__(
            self,
            file: str,
            mode: str = "r", playback_speed: float = float("inf"),
            av_params: Optional[dict] = None
    ):
        super(PyAVSource, self).__init__(playback_speed=playback_speed)

        self._mode = mode
        self._file = file
        self._av_params = av_params if av_params is not None else {}
        self._frame_topic = Topic(name="frame", dtype=Image.Image)
        self._handle = None

    def on_start(self):
        """ Initialize the file/device handle. """
        self._handle = av.open(self._file, **self._av_params)

    def on_update(self) -> Optional[MSPDataFrame]:
        try:
            frame, frame_time = next(self.frame_gen())
            return MSPDataFrame(topic=self._frame_topic, data=frame, timestamp=frame_time)
        except av.error.EOFError as e:
            return

    def frame_gen(self):
        """
        Generator for iterating over frames of the video file
        """
        stream = self._handle.streams.video[0]
        for frame in self._handle.decode(stream):
            img = frame.to_image()
            yield img, frame.time

    def on_stop(self):
        """ Close the file/device handle. """
        self._handle.close()

    @property
    def output_topics(self) -> Optional[List[Topic]]:
        return [self._frame_topic]