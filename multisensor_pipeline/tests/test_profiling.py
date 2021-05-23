import unittest
from random import randint
from time import sleep
from typing import List

from multisensor_pipeline.dataframe.dataframe import MSPDataFrame
from multisensor_pipeline.modules.base.profiling import MSPModuleStats


class ProfilingTest(unittest.TestCase):
    def test_frequency_stats(self):
        msp_stats = MSPModuleStats()
        frames: List = []
        for _ in range(20):
            frames.append(MSPDataFrame(topic="test",  value=randint(0, 20)))

        for frame in frames:
            msp_stats.add_frame(frame, direction=MSPModuleStats.Direction.IN)
            sleep(0.05)

        stats = msp_stats.get_stats(direction=MSPModuleStats.Direction.IN)
        assert 9 < stats["test"]._cma <= 20
        assert 9 < stats["test"]._sma <= 20

    def _test_frequency_stats_again(self):
        msp_stats = MSPModuleStats()
        frames = []
        # FIXME: error with more than 20 samples
        for _ in range(0, 100):
            frames.append(MSPDataFrame(topic="test",  value=randint(0, 20)))

        for frame in frames:
            msp_stats.add_frame(
                frame=frame,
                direction=MSPModuleStats.Direction.IN,
            )
            sleep(0.05)

        _ = msp_stats.get_stats(direction=MSPModuleStats.Direction.IN)
