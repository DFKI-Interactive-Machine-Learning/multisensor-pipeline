import unittest
from time import sleep

from multisensor_pipeline.dataframe import Topic
from multisensor_pipeline.modules import QueueSink
from multisensor_pipeline.modules.npy import RandomArraySource
from multisensor_pipeline.modules.signal.filtering import OneEuroProcessor
from multisensor_pipeline.modules.signal.sampling import DownsamplingProcessor
from multisensor_pipeline.pipeline.graph import GraphPipeline
import numpy as np


class DownSamplingProcessorTest(unittest.TestCase):
    def test_down_sampling_processor_no_downsampling(self):
        pipeline = self.down_sampling_processor_no_downsampling()
        for sink in pipeline.sink_nodes:
            self.assertEqual(100, sink.queue.qsize())

    def test_down_sampling_processor_no_downsampling_topic_filtered(self):
        pipeline = self.down_sampling_processor_no_downsampling(topic=Topic(name="random", dtype=int))
        for sink in pipeline.sink_nodes:
            self.assertEqual(100, sink.queue.qsize())

    def down_sampling_processor_no_downsampling(self, num_samples=100, topic=None):
        # Mock a setup like so:
        # sink_0 <- source -> processor -> sink_1

        # (1) define the modules
        source = RandomArraySource(
            shape=None,
            sampling_rate=num_samples,
            max_count=num_samples,
        )
        processor = DownsamplingProcessor(sampling_rate=num_samples * 2, topic_names=[source.output_topics[0].name])
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
        sleep(5)
        pipeline.stop()
        pipeline.join()

        return pipeline

    def test_down_sampling_processor_strong(self):
        pipeline = self.down_sampling_processor_strong()
        for sink in pipeline.sink_nodes:
            # Assert
            # There should be at most one frame for each second
            assert sink.queue.qsize() <= 2

    def test_down_sampling_processor_strong_filtered(self):
        pipeline = self.down_sampling_processor_strong(topics=[Topic(name="random", dtype=int),
                                                       Topic(name="random.1Hz", dtype=int)])
        for sink in pipeline.sink_nodes:
            # Assert
            # There should be at most one frame for each second
            assert sink.queue.qsize() <= 2

    def down_sampling_processor_strong(self, topics=None):
        # Mock a setup like so:
        # source -> processor -> sink

        # (1) define the modules
        source = RandomArraySource(
            shape=None,
            sampling_rate=100,
            max_count=100,
        )
        if topics:
            processor = DownsamplingProcessor(sampling_rate=1, topic_names=["random"])
        else:
            processor = DownsamplingProcessor(sampling_rate=1)
        sink = QueueSink()

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

        return pipeline

    def test_one_euro(self):
        pipeline = self.one_euro_filter()
        for sink in pipeline.sink_nodes:
            self.assertEqual(10, sink.queue.qsize())

    def test_one_euro_filtered(self):
        pipeline = self.one_euro_filter(topics=[Topic(name="random", dtype=np.ndarray),
                                                Topic(name="random.smoothed", dtype=np.ndarray)])
        for sink in pipeline.sink_nodes:
            self.assertEqual(10, sink.queue.qsize())

    def one_euro_filter(self, topics = None):
        # Mock a setup like so:
        # sink_0 <- source -> processor -> sink_1

        # (1) define the modules
        source = RandomArraySource(
            shape=(2,),
            sampling_rate=100,
            max_count=10,
        )
        processor = OneEuroProcessor(
            signal_topic_name="random",
            signal_key="value",
        )
        sink_1 = QueueSink()
        sink_0 = QueueSink()

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
        sleep(5)
        pipeline.stop()
        pipeline.join()

        return pipeline
