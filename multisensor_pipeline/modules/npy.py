import numpy as np
from multisensor_pipeline.modules import BaseProcessor
from multisensor_pipeline.modules.base.sampler import BaseFixedRateSource
from multisensor_pipeline.dataframe import MSPDataFrame
from typing import Optional


class RandomArraySource(BaseFixedRateSource):

    def __init__(self, shape=None, min: int = 0, max: int = 100, sampling_rate: float = 1.):
        super(RandomArraySource, self).__init__(sampling_rate)
        self._shape = shape
        self._min = min
        self._max = max

        # define what is offered
        dtype = int if shape is None else np.ndarray
        self._topic = self._generate_topic(name="random", dtype=dtype)

    def on_update(self) -> Optional[MSPDataFrame]:
        return MSPDataFrame(topic=self._topic, value=np.random.randint(self._min, self._max, size=self._shape))


class ArrayManipulationProcessor(BaseProcessor):

    def __init__(self, numpy_operation):
        super().__init__()
        self._op = numpy_operation

    def on_update(self, frame: MSPDataFrame) -> Optional[MSPDataFrame]:
        value = self._op(frame['value'])
        topic = self._generate_topic(name=f"{frame.topic.name}.{self._op.__name__}", dtype=type(value))
        return MSPDataFrame(topic=topic, value=value)
