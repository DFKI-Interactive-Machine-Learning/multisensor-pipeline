import numpy as np

from multisensor_pipeline.dataframe.dataframe import TopicEnum
from multisensor_pipeline.modules import BaseProcessor
from multisensor_pipeline.modules.base.sampler import BaseFixedRateSource
from multisensor_pipeline.dataframe import MSPDataFrame, Topic
from typing import Optional, List


class RandomArraySource(BaseFixedRateSource):

    class OutputTopics(TopicEnum):
        random_int = Topic("random", dtype=int)
        random_array = Topic("random", dtype=np.ndarray)

    def __init__(self, shape=None, min: int = 0, max: int = 100, sampling_rate: float = 1., max_count=float("inf")):
        super(RandomArraySource, self).__init__(sampling_rate)
        self._shape = shape
        self._min = min
        self._max = max
        self.max_count = max_count
        self.index = 0

    def on_update(self) -> Optional[MSPDataFrame]:
        if self.index < self.max_count:
            self.index += 1
            return MSPDataFrame(
                topic=self.OutputTopics.random_int if self._shape is None else self.OutputTopics.random_array,
                value=np.random.randint(self._min, self._max, size=self._shape)
            )
        return


class ArrayManipulationProcessor(BaseProcessor):

    def __init__(self, numpy_operation):
        super().__init__()
        self._op = numpy_operation

    def on_update(self, frame: MSPDataFrame) -> Optional[MSPDataFrame]:
        value = self._op(frame['value'])
        topic = self._generate_topic(name=f"{frame.topic.name}.{self._op.__name__}", dtype=type(value))
        return MSPDataFrame(topic=topic, value=value)
