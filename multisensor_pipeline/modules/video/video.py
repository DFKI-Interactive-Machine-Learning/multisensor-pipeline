from typing import Optional, List
import av
import cv2
from PIL.Image import Image
import numpy as np

from multisensor_pipeline import BaseSink
from multisensor_pipeline.dataframe import MSPDataFrame, Topic
from multisensor_pipeline.modules.persistence.dataset import BaseDatasetSource


class VideoSource(BaseDatasetSource):
    """
    Source for video file input. Sends PIL frames.
    """

    def __init__(self, file_path: str = "", **kwargs):
        """
        Args:
            file_path: video file path
            kwargs: kwargs for BaseDa
        """
        super(VideoSource, self).__init__(**kwargs)
        self.file_path = file_path
        self.video = None
        self.queue = None
        self._frame_topic = self._generate_topic(name="frame", dtype=Image)

    def on_start(self):
        """
        Initialize video container with the provided path.
        """
        self.video = av.open(self.file_path)

    def frame_gen(self):
        """
        Generator for iterating over frames of the video file
        """
        stream = self.video.streams.video[0]
        for frame in self.video.decode(stream):
            img = frame.to_image()
            yield img

    def on_update(self) -> Optional[MSPDataFrame]:
        try:
            frame = next(self.frame_gen())
            return MSPDataFrame(topic=self._frame_topic, data=frame)
        except av.error.EOFError as e:
            return

    def on_stop(self):
        self.video.close()

    @property
    def output_topics(self) -> Optional[List[Topic]]:
        return [self._frame_topic]


class VideoSink(BaseSink):
    """
    Sink to export PIL-Images to a video file and/or show a live preview
    """

    def __init__(self, file_path: str = "output.mp4", live_preview: bool = True, **kwargs):
        """
        Args:
            file_path: path of the export video
            live_preview: if a live preview should be shown (does not run on Mac OSX)
            topic_name: name of the frame topic
        """
        super(VideoSink, self).__init__(**kwargs)
        self.file_path = file_path
        self.live_preview = live_preview
        self.output = av.open(self.file_path, "w")
        self.stream = self.output.add_stream('h264')
        self._frame_topic = Topic(name="frame", dtype=Image)

    def on_update(self, frame: MSPDataFrame):
        """
        Writes to the video file
        """
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
        """
        Stops the VideoSink and closes the filestream
        """
        self.output.mux(self.stream.encode())
        self.output.close()

    def input_topics(self) -> List[Topic]:
        return [self._frame_topic]
