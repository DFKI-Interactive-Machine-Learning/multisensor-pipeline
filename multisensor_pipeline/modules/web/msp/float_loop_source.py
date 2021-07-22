from multisensor_pipeline.modules.base.sampler import BaseFixedRateSource
from multisensor_pipeline.dataframe import MSPDataFrame
from typing import Tuple


class FloatLoopSource(BaseFixedRateSource):

    def __init__(self, floats: Tuple, sampling_rate: float = 1.):
        """
        Repeat a list of floats at a fixed rate.

        @param floats: List of floats to loop over.
        """
        super(FloatLoopSource, self).__init__(sampling_rate=sampling_rate)

        self._topic = self._generate_topic(name="LoopedFloat", dtype=float)

        self._floats: Tuple = floats
        self._index = 0

    def on_update(self) -> MSPDataFrame:
        # Take value from floats at index, update index
        value = self._floats[self._index]
        self._index = (self._index + 1) % len(self._floats)

        frame: MSPDataFrame = \
            MSPDataFrame(
                topic=self._topic,
                value=value,
            )

        return frame
