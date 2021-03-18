from multisensor_pipeline.modules.base import BaseProcessor
from .utils import roi_rect, scale_to_image_coordinate


def crop(img, norm_pos, crop_size):
    if img is None:
        return None

    h, w = img.shape[0], img.shape[1]
    pos = scale_to_image_coordinate(norm_pos, w, h, flip_y=False)

    rect = roi_rect(width=w, height=h, center_x=pos[0], center_y=pos[1], size=crop_size)
    if rect is None:
        return None

    x1, y1, x2, y2 = rect
    return img[y1:y2, x1:x2]


class CropByPointProcessor(BaseProcessor):

    def __init__(self, image_topics, point_topics, crop_size=200, image_key="rgb", point_key=b"norm_pos"):
        super().__init__()
        self.crop_size = crop_size
        self._image = None

        # set topics to be handled and dict keys to access the correct data fields
        # TODO: if a topic is set to None, consider all topics that include the correct key
        self._image_topics = image_topics
        self._image_key = image_key
        self._crop_signal_topics = point_topics
        self._crop_signal_key = point_key

    def _update(self, frame=None):
        while self._active:
            # blocking access to data in queue
            dtype, data = self.get()
            payload = data["data"]

            # update internal temporary fields
            if any([dtype == t for t in self._image_topics]):
                self._image = payload[self._image_key]
            elif any([dtype == t for t in self._crop_signal_topics]):
                # for each crop signal -> crop image patch and notify observers
                img_patch = crop(self._image, payload[self._crop_signal_key], self.crop_size)
                if img_patch is not None:
                    p = {
                        b'base_data': payload,
                        b'base_topic': dtype,
                        b'crop_size': self.crop_size,
                        b'timestamp': payload[b'timestamp'],
                        'img_patch': img_patch
                    }
                    self._notify("eyetracking.mobile.frame.image_patch", p)
