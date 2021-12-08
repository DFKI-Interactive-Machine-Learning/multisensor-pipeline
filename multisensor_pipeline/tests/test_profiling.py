import unittest
from random import randint
from time import sleep
from typing import List, Tuple

from multisensor_pipeline import GraphPipeline, BaseSink
from multisensor_pipeline.dataframe.dataframe import MSPDataFrame, Topic
from multisensor_pipeline.modules import ListSink
from multisensor_pipeline.modules.base.profiling import MSPModuleStats
from multisensor_pipeline.modules.npy import RandomArraySource
from multisensor_pipeline.modules.signal import DownsamplingProcessor
import numpy as np


def _run_profiling(topics=None):
    # Mock a setup like so:
    # sink_0 <- source -> processor -> sink_1

    # (1) define the modules
    source_0 = RandomArraySource(
        shape=(2,),
        sampling_rate=10,
        max_count=100,
    )

    source_1 = RandomArraySource(
        sampling_rate=50,
        max_count=100,
    )

    processor = DownsamplingProcessor(sampling_rate=10)
    sink = ListSink()

    # (2) add module to a pipeline...
    pipeline = GraphPipeline(profiling=True)
    pipeline.add_source(source_0)
    pipeline.add_source(source_1)
    pipeline.add_processor(processor)
    pipeline.add_sink(sink)

    # (3) ...and connect the modules
    pipeline.connect(source_0, sink, topics=topics[0] if topics is not None else None)
    pipeline.connect(source_1, processor, topics=topics[1] if topics is not None else None)
    pipeline.connect(processor, sink, topics=topics[2] if topics is not None else None)

    # Test
    pipeline.start()
    sleep(2)
    pipeline.stop()
    pipeline.join()

    return pipeline


def _run_simple_profiling(topics=None):
    # (1) define the modules
    source = RandomArraySource(
        shape=(2,),
        sampling_rate=10,
        max_count=100,
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
    sleep(1)
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

        self.assertAlmostEqual(10, stats[topic.uuid]._cma, delta=1)
        self.assertAlmostEqual(10, stats[topic.uuid]._sma, delta=1)

    def test_simple_profiling(self):
        topic = Topic(name="random", dtype=np.ndarray)
        pipeline = _run_simple_profiling()
        for sink in pipeline.sink_nodes:
            stats = sink.stats.get_stats(direction=1, topic=topic)
            self.assertAlmostEqual(10, stats._cma, delta=1)
            self.assertAlmostEqual(10, stats._sma, delta=1)

        for source in pipeline.source_nodes:
            stats = source.stats.get_stats(direction=0, topic=topic)
            self.assertAlmostEqual(10, stats._cma, delta=1)
            self.assertAlmostEqual(10, stats._sma, delta=1)

    def test_simple_profiling_filtered(self):
        topic = Topic(name="random", dtype=np.ndarray)
        pipeline = _run_simple_profiling(topics=[topic])
        for sink in pipeline.sink_nodes:
            stats = sink.stats.get_stats(direction=1, topic=topic)
            self.assertAlmostEqual(10, stats._cma, delta=1)
            self.assertAlmostEqual(10, stats._sma, delta=1)

        for source in pipeline.source_nodes:
            stats = source.stats.get_stats(direction=0, topic=topic)
            self.assertAlmostEqual(10, stats._cma, delta=1)
            self.assertAlmostEqual(10, stats._sma, delta=1)

    def test_profiling(self):
        topic_0 = Topic(name="random", dtype=np.ndarray)
        topic_1 = Topic(name="random", dtype=int)
        topic_2 = Topic(name="random.10Hz", dtype=int)
        pipeline = _run_profiling()
        self.verify_profiling(pipeline, [topic_0, topic_1, topic_2])

    def test_profiling_filtered(self):
        topic_0 = Topic(name="random", dtype=np.ndarray)
        topic_1 = Topic(name="random", dtype=int)
        topic_2 = Topic(name="random.10Hz", dtype=int)
        pipeline = _run_profiling([topic_0, topic_1, topic_2])
        self.verify_profiling(pipeline, [topic_0, topic_1, topic_2])

    def verify_profiling(self, pipeline, topics:List[Topic]):
        sink = pipeline.sink_nodes[0]
        stats = sink.stats.get_stats(direction=1, topic=topics[0])
        self.assertAlmostEqual(10, stats._cma, delta=1)
        self.assertAlmostEqual(10, stats._sma, delta=1)
        stats = sink.stats.get_stats(direction=1, topic=topics[2])
        self.assertAlmostEqual(10, stats._cma, delta=1)
        self.assertAlmostEqual(10, stats._sma, delta=1)

        source_0 = pipeline.source_nodes[0]
        source_1 = pipeline.source_nodes[1]

        stats = source_0.stats.get_stats(direction=0, topic=topics[0])
        self.assertAlmostEqual(10, stats._cma, delta=1)
        self.assertAlmostEqual(10, stats._sma, delta=1)

        stats = source_1.stats.get_stats(direction=0, topic=topics[1])
        self.assertAlmostEqual(50, stats._cma, delta=10)
        self.assertAlmostEqual(50, stats._sma, delta=10)
