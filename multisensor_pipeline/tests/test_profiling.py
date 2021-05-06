import unittest
from random import  randint
from time import sleep

from multisensor_pipeline import GraphPipeline
from multisensor_pipeline.dataframe import MSPDataFrame
from multisensor_pipeline.modules import QueueSink
from multisensor_pipeline.modules.base.profiling import MSPModuleStats
from multisensor_pipeline.modules.npy import RandomArraySource


class ProfilingTest(unittest.TestCase):
    def _test_frequency_stats(self):
        msp_stats = MSPModuleStats()
        frames = []
        for x in range(0, 20):
            frames.append(MSPDataFrame(topic="test",  value=randint(0, 20)))

        for frame in frames:
            msp_stats.add_frame(frame, direction=MSPModuleStats.Direction.IN)
            sleep(0.05)

        stats = msp_stats.get_stats(direction=MSPModuleStats.Direction.IN)
        self.assertLessEqual(stats["test"]._cma, 20) and self.assertGreater(stats["test"]._cma, 19)
        self.assertLessEqual(stats["test"]._sma, 20) and self.assertGreater(stats["test"]._sma, 19)

    def _test_frequency_stats(self):
        msp_stats = MSPModuleStats()
        frames = []
        # FIXME: error with more than 20 samples
        for x in range(0, 100):
            frames.append(MSPDataFrame(topic="test",  value=randint(0, 20)))

        for frame in frames:
            msp_stats.add_frame(frame, direction=MSPModuleStats.Direction.IN)
            sleep(0.05)

        stats = msp_stats.get_stats(direction=MSPModuleStats.Direction.IN)
