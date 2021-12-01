from multisensor_pipeline import BaseProcessor
from multisensor_pipeline.dataframe import MSPDataFrame, Topic
from multisensor_pipeline.modules.signal.one_euro_filter import OneEuroFilter
from typing import Optional, List, Tuple
import logging
import numpy as np


logger = logging.getLogger(__name__)


class OneEuroProcessor(BaseProcessor):
    """
    Applies the 1€ smoothing filter on a continuous signal.
    http://cristal.univ-lille.fr/~casiez/1euro/

    To minimize jitter and lag when tracking human motion, the two parameters (fcmin and beta) can be set using a
    simple two-step procedure. First beta is set to 0 and fcmin (mincutoff) to a reasonable middle-ground value such
    as 1 Hz. Then the body part is held steady or moved at a very low speed while fcmin is adjusted to remove jitter
    and preserve an acceptable lag during these slow movements (decreasing fcmin reduces jitter but increases lag,
    fcmin must be > 0). Next, the body part is moved quickly in different directions while beta is increased with a
    focus on minimizing lag. First find the right order of magnitude to tune beta, which depends on the kind of data
    you manipulate and their units: do not hesitate to start with values like 0.001 or 0.0001. You can first
    multiply and divide beta by factor 10 until you notice an effect on latency when moving quickly. Note that
    parameters fcmin and beta have clear conceptual relationships: if high speed lag is a problem, increase beta;
    if slow speed jitter is a problem, decrease fcmin.
    """

    def __init__(self, signal_topic_name, signal_key, freq=30, fcmin=1.5, beta=.001, dcutoff=1):
        super(OneEuroProcessor, self).__init__()

        self._signal_topic_name = signal_topic_name
        self._signal_key = signal_key
        config = {
            'freq': freq,  # Hz
            'mincutoff': fcmin,
            'beta': beta,
            'dcutoff': dcutoff  # this one should be ok
        }
        self._filter_x = OneEuroFilter(**config)
        self._filter_y = OneEuroFilter(**config)
        self._last_timestamp = None

    def _filter(self, point, timestamp):
        if self._last_timestamp is not None and self._last_timestamp >= timestamp:
            return None
        self._last_timestamp = timestamp
        return self._filter_x(point[0], timestamp), self._filter_y(point[1], timestamp)

    def on_update(self, frame: MSPDataFrame) -> Optional[MSPDataFrame]:
        if frame.topic.name == self._signal_topic_name:
            smoothed_point = self._filter(frame.data, frame.timestamp)
            if smoothed_point is not None:
                frame.data = smoothed_point
                frame.topic = self.output_topics[0] if frame.topic.dtype == Tuple[float, float] else self.output_topics[1]
                return frame

    @property
    def input_topics(self) -> List[Topic]:
        return [Topic(name=self._signal_topic_name, dtype=Tuple[float, float]),
                Topic(name=self._signal_topic_name, dtype=np.ndarray)]

    @property
    def output_topics(self) -> Optional[List[Topic]]:
        return [Topic(name=f"{self._signal_topic_name}.smoothed", dtype=Tuple[float, float]),
                Topic(name=f"{self._signal_topic_name}.smoothed", dtype=np.ndarray)]
