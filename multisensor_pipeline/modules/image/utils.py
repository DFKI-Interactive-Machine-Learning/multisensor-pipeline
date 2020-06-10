def scale_to_image_coordinate(norm_pos, width, height, flip_y=False):
    """Scales normalized coordinates to the image coordinate system."""
    pos = [norm_pos[0] * width, norm_pos[1] * height]
    if flip_y:
        pos[1] = height - pos[1]
    return pos


def roi_rect(width, height, center_x, center_y, size):
    """Returns a tuple defining a box with edge size `size` around a center point"""
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

    return x, y, x+size, y+size
