from multisensor_pipeline.utils.dataframe import MSPDataFrame, MSPEventFrame


class MSPGazeFrame(MSPDataFrame):
    """
    Data structure for gaze data. It enforces
    (1) that the origin of gaze coordinates is at the upper left, and
    (2) the gaze coordinates are normalized.
    """

    # see also https://pillow.readthedocs.io/en/stable/handbook/concepts.html#coordinate-system
    ORIGIN_BOTTOM_LEFT = "bl"
    ORIGIN_TOP_LEFT = "tl"
    ORIGIN_CENTER = "c"

    def __init__(self, gaze, max_width=1., max_height=1., normalized=True, origin="bl", **kwargs):

        self._normalized = normalized
        self._origin = origin
        init_dict = kwargs["init_dict"] if "init_dict" in kwargs else None
        self._set_attr_from_value_or_dict("max_width", max_width, init_dict)
        self._set_attr_from_value_or_dict("max_height", max_height, init_dict)
        self._set_attr_from_value_or_dict("gaze", self._scale_gaze(gaze), init_dict)
        super(MSPGazeFrame, self).__init__(**kwargs)

    def _scale_gaze(self, gaze):
        if self._origin == self.ORIGIN_CENTER:
            raise NotImplementedError()

        x, y = tuple(gaze)
        if not self._normalized:
            x /= float(self.max_width)
            y /= float(self.max_height)

        if self._origin == self.ORIGIN_BOTTOM_LEFT:
            # convert to top-left coordinate
            y = 1. - y

        return (x, y)

    @property
    def x(self):
        return self['gaze'][0]

    @property
    def y(self):
        return self['gaze'][1]

    @property
    def gaze(self):
        return self['gaze']

    @property
    def x_scaled(self):
        return self.x * self.max_width

    @property
    def y_scaled(self):
        return self.y * self.max_height

    @property
    def gaze_scaled(self):
        return self.x_scaled, self.y_scaled

    @property
    def max_width(self):
        return self["max_width"]

    @property
    def max_height(self):
        return self["max_height"]


class MSPFixationFrame(MSPEventFrame):

    def __init__(self, fixation_position: MSPGazeFrame = None, **kwargs):
        init_dict = kwargs["init_dict"] if "init_dict" in kwargs else None
        self._set_attr_from_value_or_dict("fixation_position", fixation_position, init_dict)
        gaze = fixation_position.gaze if fixation_position is not None else None
        self._set_attr_from_value_or_dict("gaze", gaze, init_dict)
        super(MSPFixationFrame, self).__init__(**kwargs)

    @property
    def fixation_position(self) -> MSPGazeFrame:
        return self["fixation_position"]
