from PIL import Image, ImageOps
from multisensor_pipeline.modules.base import BaseProcessor
from multisensor_pipeline.dataframe.dataframe import MSPDataFrame
from typing import Optional
import numpy as np


class ImageProcessor(BaseProcessor):
    """
    Processor which applies an filter to an image.
    The filter modes are:
    s : standard
    i : inverted
    g : gradient
    b : black & white
    """
    _modes = ['s', 'i', 'g', 'b']

    def __init__(self, image_topic_name: str = 'frame', filter_topic_name: str = 'keyboard.press', filter_topic_key: str = 'key', image_key: str = 'image'):
        """
        Args:
            image_topic_name: name of image_topic
            filter_topic_name: name of filter_topic
            filter_topic_key: name of filter_topic_key
            image_key: name of image_key
        """
        super(ImageProcessor, self).__init__()
        self._image = None
        self._mode = 's'
        self._image_topic_name = image_topic_name
        self._image_key = image_key
        self._filter_topic_name = filter_topic_name
        self._filter_topic_key = filter_topic_key

    def apply_filter(self, image):
        """
        This function will apply a filter to the image and will return it.
        Args:
            image: PIL image
        """
        if self._mode == 's':
            # return the standard-image
            return image
        elif self._mode == 'i':
            # return inverted image
            return ImageOps.invert(image)
        elif self._mode == 'g':
            # calculate image-gradient
            g_y, g_x = np.gradient(np.array(ImageOps.grayscale(image)))
            # return image-gradient as Image
            return Image.fromarray(g_y+g_x).convert('L')
        elif self._mode == 'b':
            # return black&white-image
            return image.convert('L')
        pass

    def on_update(self, frame: MSPDataFrame) -> Optional[MSPDataFrame]:
        # checks if the MSDataFrame contains an image
        if frame.topic.name == self._image_topic_name:
            # get image from MSDataFrame
            img = frame['chunk']['frame']
            # apply filter
            self._image = self.apply_filter(img)
            # send the modified image to the next module in pipeline
            return MSPDataFrame(topic=self._generate_topic(name="frame", dtype=str),
                                chunk={"frame": self._image})

        # checks if the MSDataFrame contains a filter_key
        elif frame.topic.name == self._filter_topic_name:
            # get the filter_key
            key = frame['chunk'][self._filter_topic_key]
            try:
                # check if the filter_key is valid
                if key.char in self._modes:
                    # set _mode to new filter_key
                    self._mode = key.char
            except AttributeError as e:
                # if key has no char -> catch exception
                # e.g. key.escape has no 'char' value and it will throw an exception
                pass
