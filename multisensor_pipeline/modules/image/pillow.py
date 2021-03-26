from PIL import Image, ImageFile
from multisensor_pipeline.modules.base import BaseProcessor
from .utils import roi_rect, scale_to_image_coordinate
from multisensor_pipeline.dataframe.dataframe import MSPDataFrame

ImageFile.LOAD_TRUNCATED_IMAGES = True


class CropByPointerProcessor(BaseProcessor):

    def __init__(self, image_topic_name, pointer_topic_names, crop_size=200, image_key="image", point_key="gaze"):
        super(CropByPointerProcessor, self).__init__()
        self.crop_size = crop_size
        self._image = None

        # set dtypes to be handled and dict keys to access the correct data fields
        # TODO: if a dtype is set to None, consider all topics that include the correct key
        self._image_topic_name = image_topic_name
        self._image_key = image_key  # should always be "image" because it's the default for transferring images
        self._crop_signal_topic_names = pointer_topic_names
        self._crop_signal_key = point_key

    @staticmethod
    def crop(image: Image, norm_pos, crop_size: int):
        if image is None:
            return None
        w, h = image.size
        pos = scale_to_image_coordinate(norm_pos, w, h, flip_y=False)
        rect = roi_rect(width=w, height=h, center_x=pos[0], center_y=pos[1], size=crop_size)
        if rect is None:
            return None
        return image.crop(rect)

    def _update(self, frame: MSPDataFrame = None):
        # update internal temporary fields
        if frame.topic.dtype == self._image_topic_name:
            img = frame[self._image_key]
            self._image = img
        elif any([frame.topic.name == t for t in self._crop_signal_topic_names]):
            # for each crop signal -> crop image patch and notify observers
            norm_pos = frame[self._crop_signal_key]
            img_patch = self.crop(self._image, norm_pos, self.crop_size)
            if img_patch is None:
                return None

            return MSPDataFrame(topic=self._generate_topic(f"{frame.topic.name}.cropped"),
                                timestamp=frame.timestamp, image=img_patch, base_topic=frame.topic,
                                crop_size=self.crop_size)
