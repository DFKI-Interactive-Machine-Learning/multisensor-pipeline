from typing import List
import av
from PIL import Image

from .av import PyAVSource
from ..base import BaseSink
from ..persistence.dataset import BaseDatasetSource
from ...dataframe import Topic, MSPDataFrame


class VideoSource(PyAVSource, BaseDatasetSource):

    def __init__(self, file: str, playback_speed: float = 1.):
        super(VideoSource, self).__init__(file=file, playback_speed=playback_speed)


class VideoSink(BaseSink):
    """
    Sink to export PIL-Images to a video file and/or show a live preview
    """

    def __init__(self, file_path: str = "output.mp4", **kwargs):
        """
        Args:
            file_path: path of the export video
            live_preview: if a live preview should be shown (does not run on Mac OSX)
            topic_name: name of the frame topic
        """
        super(VideoSink, self).__init__(**kwargs)
        self.file_path = file_path
        self.output = av.open(self.file_path, "w")
        self.stream = self.output.add_stream('h264')
        self._frame_topic = Topic(name="frame", dtype=Image.Image)

    def on_update(self, frame: MSPDataFrame):
        """
        Writes to the video file
        """
        pil_frame = frame.data
        video_frame = av.VideoFrame.from_image(pil_frame)
        packet = self.stream.encode(video_frame)
        self.output.mux(packet)

    def on_stop(self):
        """
        Stops the VideoSink and closes the filestream
        """
        self.output.mux(self.stream.encode())
        self.output.close()

    @property
    def input_topics(self) -> List[Topic]:
        return [self._frame_topic]
