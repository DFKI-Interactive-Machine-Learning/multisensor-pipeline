import unittest
import time
import numpy as np
from multisensor_pipeline import BaseSink, GraphPipeline
from multisensor_pipeline.modules.npy import RandomArraySource
from multisensor_pipeline.dataframe import MSPDataFrame


class FixedRateGeneration(unittest.TestCase):

    def test_fixed_rate_source_under_load(self):

        class TimestampListSink(BaseSink):

            def __init__(self):
                super(TimestampListSink, self).__init__()
                self.send_timestamps = []
                self.arrival_timestamps = []

            def on_update(self, frame: MSPDataFrame):
                self.send_timestamps.append(frame.timestamp)
                self.arrival_timestamps.append(time.perf_counter())

        def _run_test_pipeline(samplerate: int, shape: tuple):
            # define the modules
            source = RandomArraySource(
                shape=shape,
                samplerate=samplerate,
                max_count=samplerate
            )
            sink = TimestampListSink()

            # add module to a pipeline...
            pipeline = GraphPipeline()
            pipeline.add(modules=[source, sink])
            # ...and connect the modules
            pipeline.connect(module=source, successor=sink)

            pipeline.start()
            time.sleep(1.)
            pipeline.stop()
            pipeline.join()

            return np.array(sink.send_timestamps), np.array(sink.arrival_timestamps)

        # test timings for increasing number of array sizes and increasing samplerates
        print("starting load test for fixed rate source...")
        measurements = []
        for samplerate in [10, 100, 1000]:
            for shape in [None, (100,), (100, 100)]:
                send_timestamps, arrival_timestamps = _run_test_pipeline(samplerate=samplerate, shape=shape)
                self.assertTrue(np.all(np.diff(send_timestamps) > 0))  # must be strictly monotonic
                n = len(send_timestamps)
                step = int(samplerate / 10)  # for smoothing
                send_rates = 1. / (np.diff(send_timestamps[::step]) / step)
                arrival_rates = 1. / (np.diff(arrival_timestamps[::step]) / step)

                print(f"rate={samplerate}\t"
                      f"mean_send_rate={send_rates.mean():.3f} "
                      f"(SD={send_rates.std():.3f}, range=[{send_rates.min():.3f};{send_rates.max():.3f}])\t"
                      f"mean_arrival_rate={arrival_rates.mean():.3f} "
                      f"(SD={arrival_rates.std():.3f}, range=[{arrival_rates.min():.3f};{arrival_rates.max():.3f}])\t"
                      f"n_samples={n}\t"
                      f"array_shape={shape}")

                measurements.append((samplerate, send_rates.mean(), n))

        for rate, measured_rate, n_samples in measurements:
            self.assertAlmostEqual(rate, measured_rate, delta=.02 * rate)  # allow 2% deviation
            # runtime is 1s with maximum samples set to rate -> expected number of samples is the samplerate
            # allow deviation of 2%, but at least 1 sample
            self.assertAlmostEqual(rate, n_samples, delta=max(1, int(.02 * rate)))


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
