from PIL import Image, ImageFile
from multisensor_pipeline.modules.base import BaseProcessor
from .utils import crop
from multisensor_pipeline.dataframe.dataframe import MSPDataFrame, Topic
from typing import Optional, List, Tuple
import numpy as np

ImageFile.LOAD_TRUNCATED_IMAGES = True


class CropByPointerProcessor(BaseProcessor):

    def __init__(self, crop_size: int = 200, pointer_topic_name: Optional[str] = None):
        super(CropByPointerProcessor, self).__init__()
        self._crop_size = crop_size
        self._latest_image = None
        self._latest_image_name = None
        self._pointer_topic_name = pointer_topic_name

    def on_update(self, frame: MSPDataFrame) -> Optional[MSPDataFrame]:
        # store the latest image
        if frame.topic.dtype == Image.Image:
            self._latest_image = frame.data
            self._latest_image_name = frame.topic.name

        # crop an image patch for each point
        elif frame.topic.dtype == Tuple[int, int] or frame.topic.dtype == np.ndarray:
            img_patch = crop(self._latest_image, frame.data, self._crop_size)
            if img_patch is None:
                return None

            return MSPDataFrame(
                topic=Topic(dtype=Image.Image, name=f"{self._latest_image_name}.cropped"),
                timestamp=frame.timestamp,
                data=img_patch
            )

    @property
    def output_topics(self) -> Optional[List[Topic]]:
        return [Topic(dtype=Image.Image)]

    @property
    def input_topics(self) -> List[Topic]:
        return [Topic(dtype=Image.Image), Topic(name=self._pointer_topic_name, dtype=Tuple[int, int]),
                Topic(name=self._pointer_topic_name, dtype=np.ndarray)]
