from typing import Optional, List
from PIL.Image import Image
import av
from multisensor_pipeline import BaseSource
from multisensor_pipeline.dataframe import MSPDataFrame, Topic


class WebCamSource(BaseSource):
    """
    Source for webcam. Sends PIL frames.
    """

    def __init__(self, web_cam_format="avfoundation", web_cam_id: str = "0", options={'framerate': '30'}):
        """
        Initialize the Source
        Args:
            web_cam_format: See more information about which web_cam_format to use in https://ffmpeg.org/ffmpeg-devices.html#Input-Devices
            web_cam_id: ID of the webcam usually "0"
            options: Options is a dict and uses following format  https://ffmpeg.org/ffmpeg.html#Video-Options
        """
        super(WebCamSource, self).__init__()
        self.web_cam_id = web_cam_id
        self.web_cam_format = web_cam_format
        self.video = None
        self.queue = None
        self.options = options
        self.video = av.open(format=self.web_cam_format, file=self.web_cam_id, options=self.options)
        self.stream = self.video.streams.video[0]
        self._topic = Topic(name="frame", dtype=Image)

    def frame_gen(self):
        """
        Generator for iterating over frames of the webcam input
        """
        for frame in self.video.decode(self.stream):
            img = frame.to_image()
            yield img

    def on_update(self) -> Optional[MSPDataFrame]:
        try:
            frame = next(self.frame_gen())
            return MSPDataFrame(topic=self._topic, data={"frame": frame})
        except av.error.BlockingIOError as e:
            return

    def on_stop(self):
        self.video.close()

    def output_topics(self) -> Optional[List[Topic]]:
        return [self._topic]
