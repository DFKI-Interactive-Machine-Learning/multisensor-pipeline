import numpy as np
from numpy.random import randint
from multisensor_pipeline.modules.base import BaseSource, BaseProcessor
from multisensor_pipeline.utils.dataframe import TypeInfo
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

    def _update_loop(self):
        while self._active:
            self._notify_all(self._offers[0], np.random.randint(1, 255, size=self._shape))
            sleep(self._sleep_time)


class ArrayManipulationProcessor(BaseProcessor):

    def __init__(self, numpy_operation):
        super().__init__()
        self._op = numpy_operation

    def _update_loop(self):
        while self._active:
            dtype, data = self.get()
            payload = data["data"]
            payload = self._op(payload)
            self._notify_all(dtype + b"." + self._op.__name__.encode(), payload)
