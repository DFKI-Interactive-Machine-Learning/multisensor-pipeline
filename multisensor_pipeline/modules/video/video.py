from typing import Optional
import av
from multisensor_pipeline.dataframe import MSPDataFrame
from multisensor_pipeline.modules.persistence.dataset import BaseDatasetSource


class VideoSource(BaseDatasetSource):
    """
    Source for video file input. Sends PIL frames.
    """

    def __init__(self, file_path="", **kwargs):
        super(VideoSource, self).__init__(**kwargs)
        self.file_path = file_path
        self.video = None
        self.queue = None

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
            return MSPDataFrame(topic=self._generate_topic(name="frame", dtype=str),
                                chunk={"frame": frame})
        except av.error.EOFError as e:
            return

    def on_stop(self):
        self.video.close()

