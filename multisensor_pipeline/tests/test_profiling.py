import unittest
from random import randint
from time import sleep
from typing import List, Tuple
from multisensor_pipeline import GraphPipeline
from multisensor_pipeline.dataframe.dataframe import MSPDataFrame, Topic
from multisensor_pipeline.modules import ListSink
from multisensor_pipeline.modules.base.profiling import MSPModuleStats
from multisensor_pipeline.modules.npy import RandomArraySource
from multisensor_pipeline.modules.signal import DownsamplingProcessor
import numpy as np


def _run_profiling(topics=None, target_sampling_rate=20, runtime=2):
    # (1) define the modules
    source = RandomArraySource(
        samplerate=target_sampling_rate * 2,
        max_count=target_sampling_rate * 2 * runtime * 1.2,
    )
    processor = DownsamplingProcessor(sampling_rate=target_sampling_rate)
    sink = ListSink()

    # (2) add module to a pipeline...
    pipeline = GraphPipeline(profiling=True)
    pipeline.add_source(source)
    pipeline.add_processor(processor)
    pipeline.add_sink(sink)

    # (3) ...and connect the modules
    pipeline.connect(source, processor, topics=topics[0] if topics is not None else None)
    pipeline.connect(processor, sink, topics=topics[0] if topics is not None else None)

    # Test
    pipeline.start()
    sleep(runtime)
    pipeline.stop()
    pipeline.join()

    return pipeline


def _run_simple_profiling(topics=None, sampling_rate=25, runtime=2):
    # (1) define the modules
    source = RandomArraySource(
        shape=(2,),
        samplerate=sampling_rate,
        max_count=int(sampling_rate * runtime * 1.2),
    )
    sink = ListSink()

    # (2) add module to a pipeline...
    pipeline = GraphPipeline(profiling=True)
    pipeline.add_source(source)
    pipeline.add_sink(sink)

    # (3) ...and connect the modules
    pipeline.connect(source, sink, topics=topics[0] if topics is not None else None)

    # Test
    pipeline.start()
    sleep(runtime)
    pipeline.stop()
    pipeline.join()

    return pipeline


class ProfilingTest(unittest.TestCase):
    def test_frequency_stats(self):
        frequency = 10
        msp_stats = MSPModuleStats()
        frames: List = []
        topic = Topic(name="random", dtype=Tuple[int, int])
        for _ in range(20):
            frames.append(MSPDataFrame(topic=topic, data=randint(0, 20)))

        for frame in frames:
            msp_stats.add_frame(frame, direction=MSPModuleStats.Direction.IN)
            sleep(1. / frequency)

        stats = msp_stats.get_stats(direction=MSPModuleStats.Direction.IN)

        self.assertAlmostEqual(frequency, stats[topic.uuid]._cma, delta=1)
        self.assertAlmostEqual(frequency, stats[topic.uuid]._sma, delta=1)

    def test_simple_profiling(self):
        topic = Topic(name="random", dtype=np.ndarray)
        frequency = 25
        pipeline = _run_simple_profiling(sampling_rate=frequency)
        for sink in pipeline.sink_nodes:
            stats = sink.stats.get_stats(direction=1, topic=topic)
            self.assertAlmostEqual(frequency, stats._cma, delta=1)
            self.assertAlmostEqual(frequency, stats._sma, delta=1)

        for source in pipeline.source_nodes:
            stats = source.stats.get_stats(direction=0, topic=topic)
            self.assertAlmostEqual(frequency, stats._cma, delta=1)
            self.assertAlmostEqual(frequency, stats._sma, delta=1)

    def test_simple_profiling_filtered(self):
        topic = Topic(name="random", dtype=np.ndarray)
        frequency = 25
        pipeline = _run_simple_profiling(topics=[topic], sampling_rate=frequency)
        for sink in pipeline.sink_nodes:
            stats = sink.stats.get_stats(direction=1, topic=topic)
            self.assertAlmostEqual(frequency, stats._cma, delta=1)
            self.assertAlmostEqual(frequency, stats._sma, delta=1)

        for source in pipeline.source_nodes:
            stats = source.stats.get_stats(direction=0, topic=topic)
            self.assertAlmostEqual(frequency, stats._cma, delta=1)
            self.assertAlmostEqual(frequency, stats._sma, delta=1)

    def test_profiling(self):
        frequency = 20
        pipeline = _run_profiling(target_sampling_rate=frequency)
        for sink in pipeline.sink_nodes:
            stats = next(iter(sink.stats.get_stats(direction=1, topic=None).values()))
            self.assertAlmostEqual(frequency, stats._cma, delta=1)
            self.assertAlmostEqual(frequency, stats._sma, delta=1)
