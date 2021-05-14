from typing import Optional
import av

from multisensor_pipeline.dataframe.dataframe import MSPDataFrame
from multisensor_pipeline.modules.base.base import BaseSource


class WebCamSource(BaseSource):
    """Source for webcam. Sends PIL frames."""

    def __init__(
        self,
        web_cam_format="avfoundation",
        web_cam_id: str = "0",
        options=None,
    ):
        """
        Initialize the Source.

        Args:
            web_cam_format: See more information about which web_cam_format to
                use in https://ffmpeg.org/ffmpeg-devices.html#Input-Devices
            web_cam_id: ID of the webcam usually "0"
            options: Options is a dict and uses following format
                https://ffmpeg.org/ffmpeg.html#Video-Options
        """
        # Handle parameter values
        if options is None:
            options = {'framerate': '30'}

        super(WebCamSource, self).__init__()

        self.web_cam_id = web_cam_id
        self.web_cam_format = web_cam_format
        self.queue = None
        self.options = options
        self.video = av.open(
            format=self.web_cam_format,
            file=self.web_cam_id,
            options=self.options,
        )

    def frame_generator(self):
        """Generate frames of the webcam input."""
        stream = self.video.streams.video[0]
        for frame in self.video.decode(stream):
            img = frame.to_image()
            yield img

    def on_update(self) -> Optional[MSPDataFrame]:
        try:
            frame = next(self.frame_generator())
            msp_data_frame: MSPDataFrame = MSPDataFrame(
                topic=self._generate_topic(name="frame", dtype=str),
                chunk={"frame": frame},
            )
            return msp_data_frame
        except av.error.BlockingIOError:
            return

    def on_stop(self):
        self.video.close()
