import time

import numpy as np
from multisensor_pipeline.modules import BaseProcessor
from multisensor_pipeline.modules.base.sampling import BaseDiscreteSamplingSource
from multisensor_pipeline.dataframe import MSPDataFrame, Topic
from typing import Optional, List


class RandomArraySource(BaseDiscreteSamplingSource):

    @property
    def output_topics(self) -> List[Topic]:
        return [Topic(name="random", dtype=int if self._shape is None else np.ndarray)]

    def __init__(self, shape=None, min: int = 0, max: int = 100, samplerate: float = 1., max_count=float("inf")):
        super(RandomArraySource, self).__init__(samplerate)
        self._shape = shape
        self._min = min
        self._max = max
        self.max_count = max_count
        self.index = 0

    def on_update(self) -> Optional[MSPDataFrame]:
        if self.index < self.max_count:
            self.index += 1
            return MSPDataFrame(
                topic=self.output_topics[0],
                data=np.random.randint(self._min, self._max, size=self._shape)
            )
        return None


class ArrayManipulationProcessor(BaseProcessor):

    def __init__(self, numpy_operation):
        super().__init__()
        self._op = numpy_operation

    def on_update(self, frame: MSPDataFrame) -> Optional[MSPDataFrame]:
        data = self._op(frame.data)
        topic = self.output_topics[0] if type(data) is int else self.output_topics[1]
        return MSPDataFrame(topic=topic, data=data)

    @property
    def input_topics(self) -> List[Topic]:
        return [Topic(dtype=int), Topic(dtype=np.ndarray)]

    @property
    def output_topics(self) -> Optional[List[Topic]]:
        return [Topic(name=self._op, dtype=int), Topic(name=self._op, dtype=np.ndarray)]
