import time
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
        frequency = self._test_frequency
        msp_stats = MSPModuleStats()
        frames: List = []
        topic = Topic(name="random", dtype=Tuple[int, int])
        for _ in range(2 * frequency):
            frames.append(MSPDataFrame(topic=topic, data=randint(0, 20)))

        t_start = time.perf_counter()
        for frame in frames:
            msp_stats.add_frame(frame, direction=MSPModuleStats.Direction.IN)
            sleep(1. / frequency)  # works for low samplerates only, because sleep is not accurate for many systems
        t_dur = time.perf_counter() - t_start
        actual_rate = (2. * frequency) / t_dur

        stats = msp_stats.get_stats(direction=MSPModuleStats.Direction.IN)

        print(f"actual rate = {actual_rate:.3f} Hz \t"
              f"measured = {stats[topic.uuid].samplerate:.3f} Hz")

        self.assertAlmostEqual(actual_rate, stats[topic.uuid].samplerate, delta=1)

    def test_simple_profiling(self):
        topic = Topic(name="random", dtype=np.ndarray)
        frequency = self._test_frequency
        pipeline = _run_simple_profiling(samplerate=frequency)
        for sink in pipeline.sink_nodes:
            stats = sink.stats.get_stats(direction=MSPModuleStats.Direction.IN, topic=topic)
            print(f"Ingoing samples\t"
                  f"actual rate = {frequency:.3f} Hz \t"
                  f"measured = {stats.samplerate:.3f} Hz")
            self.assertAlmostEqual(frequency, stats.samplerate, delta=1)

        for source in pipeline.source_nodes:
            stats = source.stats.get_stats(direction=MSPModuleStats.Direction.OUT, topic=topic)
            print(f"Outgoing samples\t"
                  f"actual rate = {frequency:.3f} Hz \t"
                  f"measured = {stats.samplerate:.3f} Hz")
            self.assertAlmostEqual(frequency, stats.samplerate, delta=1)

    def test_simple_profiling_filtered(self):
        topic = Topic(name="random", dtype=np.ndarray)
        frequency = self._test_frequency
        pipeline = _run_simple_profiling(topics=[topic], samplerate=frequency)
        for sink in pipeline.sink_nodes:
            stats = sink.stats.get_stats(direction=MSPModuleStats.Direction.IN, topic=topic)
            print(f"Ingoing samples\t"
                  f"actual rate = {frequency:.3f} Hz \t"
                  f"measured = {stats.samplerate:.3f} Hz")
            self.assertAlmostEqual(frequency, stats.samplerate, delta=1)

        for source in pipeline.source_nodes:
            stats = source.stats.get_stats(direction=MSPModuleStats.Direction.OUT, topic=topic)
            print(f"Outgoing samples\t"
                  f"actual rate = {frequency:.3f} Hz \t"
                  f"measured = {stats.samplerate:.3f} Hz")
            self.assertAlmostEqual(frequency, stats.samplerate, delta=1)

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

    def verify_profiling(self, pipeline, topics: List[Topic], delta=3):
        sink = pipeline.sink_nodes[0]
        stats = sink.stats.get_stats(direction=MSPModuleStats.Direction.IN, topic=topics[0])
        print(f"Ingoing samples (sink)\t"
              f"actual rate = {2 * self._test_frequency:.3f} Hz \t"
              f"measured = {stats.samplerate:.3f} Hz \t"
              f"({topics[0].name})")
        self.assertAlmostEqual(2 * self._test_frequency, stats.samplerate, delta=delta)
        stats = sink.stats.get_stats(direction=MSPModuleStats.Direction.IN, topic=topics[2])
        print(f"Ingoing samples (sink)\t"
              f"actual rate = {self._test_frequency:.3f} Hz \t"
              f"measured = {stats.samplerate:.3f} Hz \t"
              f"({topics[2].name})")
        self.assertAlmostEqual(self._test_frequency, stats.samplerate, delta=delta)

        source = pipeline.source_nodes[0]
        stats = source.stats.get_stats(direction=MSPModuleStats.Direction.OUT, topic=topics[0])
        print(f"Outgoing samples (source)\t"
              f"actual rate = {2 * self._test_frequency:.3f} Hz \t"
              f"measured = {stats.samplerate:.3f} Hz \t"
              f"({topics[0].name})")
        self.assertAlmostEqual(2 * self._test_frequency, stats.samplerate, delta=delta)

        processor = pipeline.processor_nodes[0]
        stats = processor.stats.get_stats(direction=MSPModuleStats.Direction.OUT, topic=topics[2])
        print(f"Outgoing samples (processor)\t"
              f"actual rate = {self._test_frequency:.3f} Hz \t"
              f"measured = {stats.samplerate:.3f} Hz \t"
              f"({topics[2].name})")
        self.assertAlmostEqual(self._test_frequency, stats.samplerate, delta=delta)

        stats = processor.stats.get_stats(direction=MSPModuleStats.Direction.IN, topic=topics[1])
        print(f"Incoming samples (processor)\t"
              f"actual rate = {self._test_frequency:.3f} Hz \t"
              f"measured = {stats.samplerate:.3f} Hz \t"
              f"({topics[1].name})")
        self.assertAlmostEqual(2 * self._test_frequency, stats.samplerate, delta=delta)
