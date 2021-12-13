from ..base import BaseSink
from abc import ABC
from typing import Optional, List
import av
from PIL import Image
from multisensor_pipeline.dataframe import Topic, MSPDataFrame
from multisensor_pipeline.modules.persistence import BaseDatasetSource


class PyAVSource(BaseDatasetSource, ABC):

    def __init__(
            self, file: str, av_format: Optional[str] = None, av_options: Optional[dict] = None,
            playback_speed: float = float("inf")
    ):
        super(PyAVSource, self).__init__(playback_speed=playback_speed)

        self._file = file
        self._av_format = av_format
        self._av_options = av_options if av_options is not None else {}
        self._frame_topic = Topic(name="frame", dtype=Image.Image)
        self._container = None

    def on_start(self):
        """ Initialize the file/device handle. """
        self._container = av.open(
            file=self._file,
            format=self._av_format,
            options=self._av_options
        )

    def on_update(self) -> Optional[MSPDataFrame]:
        frame, frame_time = next(self.frame_gen())
        if frame is None:
            return None
        return MSPDataFrame(topic=self._frame_topic, data=frame, timestamp=frame_time)

    def frame_gen(self):
        """
        Generator for iterating over frames of the video file
        """
        try:
            for frame in self._container.decode(video=0):
                img = frame.to_image()
                yield img, frame.time
        except av.error.EOFError as e:
            yield None, 0
        except av.error.BlockingIOError as e:
            yield None, 0

    def on_stop(self):
        """ Close the file/device handle. """
        self._container.close()

    @property
    def output_topics(self) -> Optional[List[Topic]]:
        return [self._frame_topic]


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
