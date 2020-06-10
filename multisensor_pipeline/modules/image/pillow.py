from PIL import Image
from PIL import ImageFile
from multisensor_pipeline.modules.base import BaseProcessor
from .utils import roi_rect, scale_to_image_coordinate
from ...utils.dataframe import MSPDataFrame

ImageFile.LOAD_TRUNCATED_IMAGES = True


class CropByPointerProcessor(BaseProcessor):

    def __init__(self, image_dtype, pointer_dtypes, crop_size=200, image_key="image", point_key=b"norm_pos"):
        super().__init__()
        self.crop_size = crop_size
        self._image = None

        # set dtypes to be handled and dict keys to access the correct data fields
        # TODO: if a dtype is set to None, consider all topics that include the correct key
        self._image_dtype = image_dtype
        self._image_key = image_key  # should always be "image" because it's the default for transferring images
        self._crop_signal_dtypes = pointer_dtypes
        self._crop_signal_key = point_key

    @staticmethod
    def crop(image: Image, norm_pos, crop_size: int):
        if image is None:
            return None
        w, h = image.size
        pos = scale_to_image_coordinate(norm_pos, w, h, flip_y=True)
        rect = roi_rect(width=w, height=h, center_x=pos[0], center_y=pos[1], size=crop_size)
        if rect is None:
            return None
        return image.crop(rect)

    def _update_loop(self):
        while self._active:
            # blocking access to data in queue
            dtype, data = self.get()

            # update internal temporary fields
            if dtype == self._image_dtype:
                img = data[self._image_key]
                self._image = img
            elif any([dtype == t for t in self._crop_signal_dtypes]):
                # for each crop signal -> crop image patch and notify observers
                norm_pos = data[self._crop_signal_key]
                img_patch = self.crop(self._image, norm_pos, self.crop_size)
                if img_patch is None:
                    continue

                p = {
                    # b'base_data': data,
                    'base_topic': dtype,
                    'crop_size': self.crop_size,
                    'image': img_patch
                }
                self._notify_all(self._image_dtype, suffix="cropped",
                                 data=MSPDataFrame(timestamp=data.timestamp, init_dict=p))
