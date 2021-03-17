import numpy as np
from numpy.random import randint
from multisensor_pipeline.modules.base import BaseSource, BaseProcessor
from multisensor_pipeline.utils.dataframe import TypeInfo, MSPDataFrame
from time import sleep


class RandomArraySource(BaseSource):

    def __init__(self, shape=None, frequency=1):
        super().__init__()
        self._shape = shape
        self._sleep_time = 1./frequency

        # define what is offered
        dtype = int if shape is None else np.ndarray
        type_info = TypeInfo(dtype=dtype, name="random")
        self._offers = [type_info]

    def _update(self, frame=None):
        while self._active:
            frame = MSPDataFrame(dtype=self._offers[0])
            frame['value'] = np.random.randint(1, 255, size=self._shape)
            self._notify_all(frame)
            sleep(self._sleep_time)


class ArrayManipulationProcessor(BaseProcessor):

    def __init__(self, numpy_operation):
        super().__init__()
        self._op = numpy_operation

    def _update(self, frame=None):
        new_frame = MSPDataFrame(dtype=f"{frame.dtype}.{self._op.__name__}")
        new_frame['value'] = self._op(frame['value'])
        self._notify_all(new_frame)
