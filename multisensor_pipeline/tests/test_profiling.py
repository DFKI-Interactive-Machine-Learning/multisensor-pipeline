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


def _run_profiling(topics=None, samplerate=20, runtime=2):
    # (1) define the modules
    source = RandomArraySource(
        samplerate=samplerate * 2,
        max_count=samplerate * 2 * runtime,
    )
    processor = DownsamplingProcessor(samplerate=samplerate)
    sink = ListSink()

    # (2) add module to a pipeline...
    pipeline = GraphPipeline(profiling=True)
    pipeline.add_source(source)
    pipeline.add_processor(processor)
    pipeline.add_sink(sink)

    # (3) ...and connect the modules
    pipeline.connect(source, sink, topics=topics[0] if topics is not None else None)
    pipeline.connect(source, processor, topics=topics[1] if topics is not None else None)
    pipeline.connect(processor, sink, topics=topics[2] if topics is not None else None)

    # Test
    pipeline.start()
    sleep(runtime)
    pipeline.stop()
    pipeline.join()

    return pipeline


def _run_simple_profiling(topics=None, samplerate=25, runtime=2):
    # (1) define the modules
    source = RandomArraySource(
        shape=(2,),
        samplerate=samplerate,
        max_count=int(samplerate * runtime * 1.2),
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

    _test_frequency = 20

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
        frequency = self._test_frequency
        pipeline = _run_simple_profiling(samplerate=frequency)
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
        frequency = self._test_frequency
        pipeline = _run_simple_profiling(topics=[topic], samplerate=frequency)
        for sink in pipeline.sink_nodes:
            stats = sink.stats.get_stats(direction=1, topic=topic)
            self.assertAlmostEqual(frequency, stats._cma, delta=1)
            self.assertAlmostEqual(frequency, stats._sma, delta=1)

        for source in pipeline.source_nodes:
            stats = source.stats.get_stats(direction=0, topic=topic)
            self.assertAlmostEqual(frequency, stats._cma, delta=1)
            self.assertAlmostEqual(frequency, stats._sma, delta=1)

    def test_profiling(self):
        topic_0 = Topic(name="random", dtype=int)
        topic_1 = Topic(name="random", dtype=int)
        topic_2 = Topic(name=f"random.{self._test_frequency}Hz", dtype=int)
        pipeline = _run_profiling(samplerate=self._test_frequency)
        self.verify_profiling(pipeline, [topic_0, topic_1, topic_2])

    def test_profiling_filtered(self):
        topic_0 = Topic(name="random", dtype=int)
        topic_1 = Topic(name="random", dtype=int)
        topic_2 = Topic(name=f"random.{self._test_frequency}Hz", dtype=int)
        pipeline = _run_profiling(topics=[topic_0, topic_1, topic_2], samplerate=self._test_frequency)
        self.verify_profiling(pipeline, [topic_0, topic_1, topic_2])

    def verify_profiling(self, pipeline, topics: List[Topic], delta=1):
        sink = pipeline.sink_nodes[0]
        stats = sink.stats.get_stats(direction=1, topic=topics[0])  # IN
        self.assertAlmostEqual(2 * self._test_frequency, stats._cma, delta=delta)
        self.assertAlmostEqual(2 * self._test_frequency, stats._sma, delta=delta)
        stats = sink.stats.get_stats(direction=1, topic=topics[2])  # IN
        self.assertAlmostEqual(self._test_frequency, stats._cma, delta=delta)
        self.assertAlmostEqual(self._test_frequency, stats._sma, delta=delta)

        source = pipeline.source_nodes[0]
        stats = source.stats.get_stats(direction=0, topic=topics[0])  # OUT
        self.assertAlmostEqual(2 * self._test_frequency, stats._cma, delta=delta)
        self.assertAlmostEqual(2 * self._test_frequency, stats._sma, delta=delta)

        processor = pipeline.processor_nodes[0]
        stats = processor.stats.get_stats(direction=0, topic=topics[1])  # OUT
        self.assertAlmostEqual(self._test_frequency, stats._cma, delta=delta)
        self.assertAlmostEqual(self._test_frequency, stats._sma, delta=delta)

        stats = processor.stats.get_stats(direction=1, topic=topics[1])  # IN
        self.assertAlmostEqual(2 * self._test_frequency, stats._cma, delta=delta)
        self.assertAlmostEqual(2 * self._test_frequency, stats._sma, delta=delta)
