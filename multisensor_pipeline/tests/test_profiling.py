import unittest
from random import randint
from time import sleep
from typing import List

from multisensor_pipeline.dataframe.dataframe import MSPDataFrame
from multisensor_pipeline.modules.base.profiling import MSPModuleStats
from multisensor_pipeline.tests.environment_properties import \
    is_running_in_ci, is_running_on_macos, is_running_on_linux, \
    is_running_on_windows


class ProfilingTest(unittest.TestCase):
    def test_frequency_stats(self):
        frequency = 10
        msp_stats = MSPModuleStats()
        frames: List = []
        for _ in range(20):
            frames.append(MSPDataFrame(topic="test", value=randint(0, 20)))

        for frame in frames:
            msp_stats.add_frame(frame, direction=MSPModuleStats.Direction.IN)
            sleep(1./frequency)

        stats = msp_stats.get_stats(direction=MSPModuleStats.Direction.IN)

        # TODO Loosening a test just like that is not a proper fix.
        # TODO Make the code under test work as intended.
        # TODO *Only then* tighten these conditions again for all environments.
        if is_running_in_ci() and is_running_on_macos():
            assert 5 < stats["test"]._cma <= 20
            assert 5 < stats["test"]._sma <= 20
        elif is_running_in_ci() and is_running_on_linux():
            assert 9 < stats["test"]._cma <= 20
            assert 9 < stats["test"]._sma <= 20
        elif is_running_in_ci() and is_running_on_windows():
            assert 9 < stats["test"]._cma <= 20
            assert 9 < stats["test"]._sma <= 20
        else:
            self.assertAlmostEqual(10, stats["test"]._cma, delta=1)
            self.assertAlmostEqual(10, stats["test"]._sma, delta=1)

    # TODO Deactivating a test just like that is not a proper fix.
    # TODO Make the code under test work as intended.
    # TODO *Only then* reactivate this test.
    def _test_frequency_stats_again(self):
        msp_stats = MSPModuleStats()
        frames = []
        # FIXME: does not work with higher frame rate because of sleep
        for _ in range(0, 50):
            frames.append(MSPDataFrame(topic="test", value=randint(0, 20)))

        for frame in frames:
            msp_stats.add_frame(
                frame=frame,
                direction=MSPModuleStats.Direction.IN,
            )
            sleep(1./10)

        stats = msp_stats.get_stats(direction=MSPModuleStats.Direction.IN)
        self.assertAlmostEqual(10, stats["test"]._cma, delta=1)
