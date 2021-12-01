from typing import Tuple, Optional
from PIL import Image


def roi_rect(width: int, height: int, center_x: int, center_y: int, size: int) -> Optional[Tuple[int, int, int, int]]:
    """ Returns a tuple defining a box with edge size `size` around a center point. """
    s = int(.5 * size)
    x, y = int(center_x) - s, int(center_y) - s

    # filter gaze that is completely out of the frame
    if x < -s or y < -s or x + size > width + s - 1 or y + size > height + s - 1:
        return None

    # fit crop area for border regions
    if x < 0:
        x = 0
    elif x + size > width - 1:
        x = int(width - size - 1)
    if y < 0:
        y = 0
    elif y + size > height - 1:
        y = int(height - size - 1)

    return x, y, x + size, y + size


def crop(image: Image.Image, point: Tuple[int, int], crop_size: int) -> Optional[Image.Image]:
    """ Crops an image patch from a pillow Image. """
    if image is None:
        return None
    w, h = image.size
    rect = roi_rect(width=w, height=h, center_x=point[0], center_y=point[1], size=crop_size)
    if rect is None:
        return None
    return image.crop(rect)
