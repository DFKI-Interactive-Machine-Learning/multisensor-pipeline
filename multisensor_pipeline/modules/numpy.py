import numpy as np
from numpy.random import randint
from . import BaseSource, BaseProcessor
from ..dataframe import Topic, MSPDataFrame
from time import sleep


class RandomArraySource(BaseSource):

    def __init__(self, shape=None, frequency=1):
        super().__init__()
        self._shape = shape
        self._sleep_time = 1./frequency

        # define what is offered
        dtype = int if shape is None else np.ndarray
        self._offers = [Topic(dtype=dtype, name="random", source_module=self.__class__)]

    def _update(self) -> MSPDataFrame:
        sleep(self._sleep_time)
        return MSPDataFrame(topic=self._offers[0], value=np.random.randint(1, 255, size=self._shape))


class ArrayManipulationProcessor(BaseProcessor):

    def __init__(self, numpy_operation):
        super().__init__()
        self._op = numpy_operation

    def _update(self, frame: MSPDataFrame = None):
        value = self._op(frame['value'])
        topic = Topic(name=f"{frame.topic.name}.{self._op.__name__}", dtype=type(value), source_module=self.__class__)
        self._notify(MSPDataFrame(topic=topic, value=value))
