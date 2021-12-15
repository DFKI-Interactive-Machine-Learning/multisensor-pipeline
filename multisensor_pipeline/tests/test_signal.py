import unittest
from time import sleep
from multisensor_pipeline.dataframe import Topic
from multisensor_pipeline.modules import QueueSink, ListSink
from multisensor_pipeline.modules.npy import RandomArraySource
from multisensor_pipeline.modules.signal.filtering import OneEuroProcessor
from multisensor_pipeline.modules.signal.sampling import DownsamplingProcessor
from multisensor_pipeline.pipeline.graph import GraphPipeline
import numpy as np


class DownSamplingProcessorTest(unittest.TestCase):

    @staticmethod
    def _run_down_sampling_processor_no_downsampling_pipeline(num_samples=100, topic=None):
        # Mock a setup like so:
        # sink_0 <- source -> processor -> sink_1

        # (1) define the modules
        source = RandomArraySource(
            shape=None,
            samplerate=num_samples,
            max_count=num_samples,
        )
        processor = DownsamplingProcessor(target_topics=[source.output_topics[0]], sampling_rate=num_samples)
        sink_0 = QueueSink()
        sink_1 = QueueSink()

        # (2) add module to a pipeline...
        pipeline = GraphPipeline()
        pipeline.add_sink(sink_0)
        pipeline.add_source(source)
        pipeline.add_processor(processor)
        pipeline.add_sink(sink_1)

        # (3) ...and connect the modules
        pipeline.connect(source, sink_0)
        pipeline.connect(source, processor, topics=topic)
        pipeline.connect(processor, sink_1)

        # Test
        pipeline.start()
        sleep(1.5)
        pipeline.stop()
        pipeline.join()

        return pipeline

    def test_down_sampling_processor_no_downsampling(self):
        pipeline = self._run_down_sampling_processor_no_downsampling_pipeline()
        for sink in pipeline.sink_nodes:
            self.assertAlmostEqual(100, sink.queue.qsize(), delta=1)

    def test_down_sampling_processor_no_downsampling_topic_filtered(self):
        pipeline = self._run_down_sampling_processor_no_downsampling_pipeline(topic=Topic(name="random", dtype=int))
        for sink in pipeline.sink_nodes:
            self.assertEqual(100, sink.queue.qsize())

    @staticmethod
    def _run_down_sampling_processor_strong_pipeline(topics=None):
        # Mock a setup like so:
        # source -> processor -> sink

        # (1) define the modules
        source = RandomArraySource(
            shape=None,
            samplerate=100,
            max_count=100,
        )
        if topics:
            processor = DownsamplingProcessor(sampling_rate=1, target_topics=[Topic(name="random")])
        else:
            processor = DownsamplingProcessor(sampling_rate=1)
        sink = ListSink()

        # (2) add module to a pipeline...
        pipeline = GraphPipeline()
        pipeline.add_source(source)
        pipeline.add_processor(processor)
        pipeline.add_sink(sink)

        # (3) ...and connect the modules
        pipeline.connect(source, processor, topics=topics[0] if topics is not None else None)
        pipeline.connect(processor, sink, topics=topics[1] if topics is not None else None)

        # Test
        pipeline.start()
        sleep(2)
        pipeline.stop()
        pipeline.join()

        return sink

    def test_down_sampling_processor_strong(self):
        sink = self._run_down_sampling_processor_strong_pipeline()
        # There should be at most one frame for each second
        self.assertAlmostEqual(len(sink), 2, delta=1)

    def test_down_sampling_processor_strong_filtered(self):
        sink = self._run_down_sampling_processor_strong_pipeline(
            topics=[Topic(name="random", dtype=int),
                    Topic(name="random.1Hz", dtype=int)]
        )
        # There should be at most one frame for each second
        self.assertAlmostEqual(len(sink), 2, delta=1)

    @staticmethod
    def _run_one_euro_filter_pipeline(topics=None):
        # Mock a setup like so:
        # sink_0 <- source -> processor -> sink_1

        # (1) define the modules
        source = RandomArraySource(
            shape=(2,),
            samplerate=100,
            max_count=10,
        )
        processor = OneEuroProcessor()
        sink_1 = ListSink()
        sink_0 = ListSink()

        # (2) add module to a pipeline...
        pipeline = GraphPipeline()
        pipeline.add_source(source)
        pipeline.add_processor(processor)
        pipeline.add_sink(sink_1)
        pipeline.add_sink(sink_0)

        # (3) ...and connect the modules
        pipeline.connect(source, sink_0, topics=topics[0] if topics is not None else None)
        pipeline.connect(source, processor, topics=topics[0] if topics is not None else None)
        pipeline.connect(processor, sink_1, topics=topics[1] if topics is not None else None)

        # Test
        pipeline.start()
        sleep(.5)
        pipeline.stop()
        pipeline.join()

        return pipeline

    def test_one_euro(self):
        pipeline = self._run_one_euro_filter_pipeline()
        for sink in pipeline.sink_nodes:
            self.assertEqual(10, len(sink))

    def test_one_euro_filtered(self):
        pipeline = self._run_one_euro_filter_pipeline(
            topics=[Topic(name="random", dtype=np.ndarray),
                    Topic(name="random.smoothed", dtype=np.ndarray)]
        )
        for sink in pipeline.sink_nodes:
            self.assertEqual(10, len(sink))

    @staticmethod
    def _run_random_array(topics=None):
        # (1) define the modules
        source = RandomArraySource(
            shape=(2,),
            samplerate=100,
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
        sleep(1.15)
        pipeline.stop()
        pipeline.join()

        return pipeline

    def test_random_array_source(self):
        pipeline = self._run_random_array()
        for sink in pipeline.sink_nodes:
            self.assertEqual(100, len(sink))


