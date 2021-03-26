import numpy as np
from multisensor_pipeline.modules import BaseSource, BaseProcessor
from multisensor_pipeline.dataframe import Topic, MSPDataFrame
from time import sleep


class RandomArraySource(BaseSource):

    def __init__(self, shape=None, frequency=1):
        super().__init__()
        self._shape = shape
        self._sleep_time = 1./frequency

        # define what is offered
        dtype = int if shape is None else np.ndarray
        self._topic = self._generate_topic(name="random", dtype=dtype)

    def _update(self) -> MSPDataFrame:
        sleep(self._sleep_time)
        return MSPDataFrame(topic=self._topic, value=np.random.randint(1, 255, size=self._shape))


class ArrayManipulationProcessor(BaseProcessor):

    def __init__(self, numpy_operation):
        super().__init__()
        self._op = numpy_operation

    def _update(self, frame: MSPDataFrame = None):
        value = self._op(frame['value'])
        topic = self._generate_topic(name=f"{frame.topic.name}.{self._op.__name__}", dtype=type(value))
        self._notify(MSPDataFrame(topic=topic, value=value))
