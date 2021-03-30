import numpy as np
from multisensor_pipeline.modules import BaseProcessor
from multisensor_pipeline.modules.base.sampler import BaseFixedRateSource
from multisensor_pipeline.dataframe import MSPDataFrame


class RandomArraySource(BaseFixedRateSource):

    def __init__(self, shape=None, min: int= 0, max: int = 100, sampling_rate: float = 1):
        super(RandomArraySource, self).__init__(sampling_rate)
        self._shape = shape
        self._min = min
        self._max = max

        # define what is offered
        dtype = int if shape is None else np.ndarray
        self._topic = self._generate_topic(name="random", dtype=dtype)

    def _update(self) -> MSPDataFrame:
        return MSPDataFrame(topic=self._topic, value=np.random.randint(self._min, self._max, size=self._shape))


class ArrayManipulationProcessor(BaseProcessor):

    def __init__(self, numpy_operation):
        super().__init__()
        self._op = numpy_operation

    def _update(self, frame: MSPDataFrame = None):
        value = self._op(frame['value'])
        topic = self._generate_topic(name=f"{frame.topic.name}.{self._op.__name__}", dtype=type(value))
        self._notify(MSPDataFrame(topic=topic, value=value))
