from PIL import Image, ImageFile
from .utils import roi_rect
from multisensor_pipeline.dataframe.dataframe import MSPDataFrame
from typing import Optional

from multisensor_pipeline.modules.base.base import BaseProcessor

ImageFile.LOAD_TRUNCATED_IMAGES = True


class CropByPointerProcessor(BaseProcessor):
    """Crop PillowImage on a give point with a definable crop size."""

    def __init__(
        self,
        image_topic_name,
        pointer_topic_names,
        crop_size: int = 200,
        image_key: str = "image",
        point_key: str = "point",
    ):
        """
        Initialize the Processor.

        Args:
           image_topic_name: image topic names to be handled
           pointer_topic_names: pointer topic names to be handled
           crop_size: size of the crop AOI
           image_key: should always be "image" because it's the default for
                      transferring images
           point_key: key of the point in the signal
        """
        super(CropByPointerProcessor, self).__init__()
        self.crop_size = crop_size
        self._image = None

        # set topic names to be handled and dict keys to access the correct
        # data fields
        # TODO: if a names are set to None, consider all topics that include
        # the correct key
        self._image_topic_name = image_topic_name

        # should always be "image" because it's the default for transferring
        # images
        self._image_key = image_key

        self._crop_signal_topic_names = pointer_topic_names
        self._crop_signal_key = point_key

    @staticmethod
    def crop(image: Image, point, crop_size: int):
        """Crop the PillowImage."""
        if image is None:
            return None
        w, h = image.size

        # pos = scale_to_image_coordinate(point, w, h, flip_y=False)

        rect = roi_rect(
            width=w,
            height=h,
            center_x=point[0],
            center_y=point[1],
            size=crop_size
        )
        if rect is None:
            return None
        return image.crop(rect)

    def on_update(self, frame: MSPDataFrame) -> Optional[MSPDataFrame]:
        # update internal temporary fields
        if frame.topic.name == self._image_topic_name:
            img = frame[self._image_key]
            self._image = img
        elif any(
            [frame.topic.name == t for t in self._crop_signal_topic_names]
        ):
            # for each crop signal -> crop image patch and notify observers
            point = frame[self._crop_signal_key]
            img_patch = self.crop(self._image, point, self.crop_size)
            if img_patch is None:
                return None

            return MSPDataFrame(
                topic=self._generate_topic(
                    name=f"{self._image_topic_name}.cropped"
                ),
                timestamp=frame.timestamp,
                image=img_patch,
                base_topic=frame.topic,
                crop_size=self.crop_size,
            )
