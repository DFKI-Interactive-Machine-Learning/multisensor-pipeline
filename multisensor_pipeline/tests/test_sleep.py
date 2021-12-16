import unittest
import time

import numpy as np


class SleepTest(unittest.TestCase):
    """
    Checks how accurate your system's sleep() function works.
    This is important, if you want to generate data at a certain speed.
    We also test some alternatives for being used with MSP.
    """

    _samplerates = [1., 10., 100., 1000., 10000.]

    @staticmethod
    def _hybrid_sleep(secs: float):
        t_goal = time.perf_counter() + secs
        time.sleep(0.8*secs)
        while time.perf_counter() < t_goal:
            pass

    @staticmethod
    def _exact_sleep(secs: float):
        t_goal = time.perf_counter() + secs
        while time.perf_counter() < t_goal:
            pass

    @staticmethod
    def _measure(func, args, n=1000) -> np.ndarray:
        res = np.zeros(shape=(n,), dtype=np.float)
        for i in range(n):
            t_start = time.perf_counter()
            func(*args)
            res[i] = time.perf_counter() - t_start
        return res

    def _test_sleep_accuracy(self, sleep_func, samplerates):
        measurements = []
        for rate in samplerates:
            sleeptime = 1. / rate
            n = 1000 if sleeptime * 1000 < 5. else int(5. / sleeptime)
            t_measured = SleepTest._measure(func=sleep_func, args=(sleeptime,), n=n).mean()
            measurements.append((rate, sleeptime, t_measured))
            print(f"samplerate={rate}\tachieved={1./t_measured} (n={n})")

        for rate, sleeptime, measured_sleeptime in measurements:
            self.assertAlmostEqual(rate, 1./measured_sleeptime, delta=0.05 * rate)

    def test_system_sleep_accuracy(self):
        self._test_sleep_accuracy(time.sleep, self._samplerates)

    def test_exact_sleep_accuracy(self):
        self._test_sleep_accuracy(SleepTest._exact_sleep, self._samplerates)

    def test_hybrid_sleep_accuracy(self):
        self._test_sleep_accuracy(SleepTest._hybrid_sleep, self._samplerates)
