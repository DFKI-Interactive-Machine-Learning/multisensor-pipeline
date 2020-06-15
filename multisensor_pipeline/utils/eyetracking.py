from multisensor_pipeline.utils.dataframe import MSPDataFrame, MSPEventFrame


class MSPGazeFrame(MSPDataFrame):

    # see also https://pillow.readthedocs.io/en/stable/handbook/concepts.html#coordinate-system
    ORIGIN_BOTTOM_LEFT = "bl"
    ORIGIN_TOP_LEFT = "tl"
    ORIGIN_CENTER = "c"

    def __init__(self, gaze, max_width=1280., max_height=720., normalized=True, origin="bl", **kwargs):

        self._normalized = normalized
        self._origin = origin
        self._max_width = max_width
        self._max_height = max_height
        self._set_gaze(gaze)
        super(MSPGazeFrame, self).__init__(**kwargs)

    def _set_gaze(self, gaze):
        if self._origin == self.ORIGIN_CENTER:
            raise NotImplementedError()

        x, y = tuple(gaze)
        if not self._normalized:
            x /= float(self._max_width)
            y /= float(self._max_height)

        if self._origin == self.ORIGIN_BOTTOM_LEFT:
            y = 1.-y

        self._gaze = (x, y)

    @property
    def x(self):
        return self._gaze[0]

    @property
    def y(self):
        return self._gaze[1]

    @property
    def gaze(self):
        return self.gaze

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
        return self._max_width

    @property
    def max_height(self):
        return self._max_height


class MSPFixationFrame(MSPEventFrame):
    
    def __init__(self, fixation_position: MSPGazeFrame, **kwargs):
        self._gaze_frame = fixation_position
        super(MSPFixationFrame, self).__init__(**kwargs)

    @property
    def fixation_position(self) -> MSPGazeFrame:
        return self._gaze_frame
