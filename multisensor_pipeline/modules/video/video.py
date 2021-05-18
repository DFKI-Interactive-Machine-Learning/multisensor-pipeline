from typing import Optional
import av
import cv2
import numpy as np

from multisensor_pipeline.modules.paths import DATA_PATH
from multisensor_pipeline.dataframe.dataframe import MSPDataFrame
from multisensor_pipeline.modules import BaseSink
from multisensor_pipeline.modules.persistence.dataset import BaseDatasetSource


class VideoSource(BaseDatasetSource):
    """Source for video file input. Sends PIL frames."""

    def __init__(self, file_path: str = "", **kwargs):
        """
        Create a video source instance.

        Args:
            file_path: video file path
            kwargs: kwargs for BaseDa
        """
        super(VideoSource, self).__init__(**kwargs)
        self.file_path = file_path
        self.video = None
        self.queue = None

    def on_start(self):
        """Initialize video container with the provided path."""
        self.video = av.open(self.file_path)

    def frame_gen(self):
        """Generate frames of the video file."""
        stream = self.video.streams.video[0]
        for frame in self.video.decode(stream):
            img = frame.to_image()
            yield img

    def on_update(self) -> Optional[MSPDataFrame]:
        try:
            frame = next(self.frame_gen())
            return MSPDataFrame(
                topic=self._generate_topic(name="frame", dtype=str),
                chunk={"frame": frame},
            )
        except av.error.EOFError:
            return

    def on_stop(self):
        self.video.close()


class VideoSink(BaseSink):
    """Sink to export PIL-Images to a video file and/or show a live preview."""

    def __init__(
        self,
        file_path: str = None,
        live_preview: bool = True,
        topic_name: str = "frame",
        **kwargs,
    ):
        """
        Create an instance of a video sink.

        Args:
            file_path: path of the export video
            live_preview: if a live preview should be shown
                          (does not run on macOS)
            topic_name: name of the frame topic
        """
        super(VideoSink, self).__init__(**kwargs)

        # Handle parameter values
        if file_path is None:
            file_path = str(DATA_PATH / "output.mp4")

        self.file_path = file_path
        self.live_preview = live_preview
        self.topic_name = topic_name
        self.output = av.open(self.file_path, "w")
        self.stream = self.output.add_stream('h264')

    def on_update(self, frame: MSPDataFrame):
        """Write to the video file."""
        if frame.topic.name == self.topic_name:
            pil_frame = frame["chunk"][self.topic_name]
            video_frame = av.VideoFrame.from_image(pil_frame)
            packet = self.stream.encode(video_frame)
            self.output.mux(packet)
            if self.live_preview:
                cv_img = np.array(pil_frame)
                cv_img = cv_img[:, :, ::-1]
                cv2.startWindowThread()
                cv2.namedWindow("preview")
                cv2.imshow("preview", cv_img)
                cv2.waitKey(1)

    def on_stop(self):
        """Stop the VideoSink and closes the filestream."""
        self.output.mux(self.stream.encode())
        self.output.close()
