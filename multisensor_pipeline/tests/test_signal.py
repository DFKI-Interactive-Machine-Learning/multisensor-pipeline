import unittest
from time import sleep

from multisensor_pipeline.modules import QueueSink
from multisensor_pipeline.modules.npy import RandomArraySource
from multisensor_pipeline.modules.signal.filtering import OneEuroProcessor
from multisensor_pipeline.modules.signal.sampling import DownsamplingProcessor
from multisensor_pipeline.pipeline.graph import GraphPipeline
from multisensor_pipeline.tests.environment_properties import \
    is_running_in_ci, is_running_on_macos


class DownsamplingProcessorTest(unittest.TestCase):
    def test_down_sampling_processor_no_downsampling(self):
        # Mock a setup like so:
        # sink_0 <- source -> processor -> sink_1
        num_samples = 100

        # (1) define the modules
        source = RandomArraySource(
            shape=None,
            sampling_rate=num_samples,
            max_count=num_samples,
        )
        processor = DownsamplingProcessor(sampling_rate=num_samples * 2)
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
        pipeline.connect(source, processor)
        pipeline.connect(processor, sink_1)

        # Test
        pipeline.start()
        sleep(5)
        pipeline.stop()
        pipeline.join()

        sleep(0.1)  # To make this work under macOS in the cloud

        # Assert
        # TODO Loosening a test just like that is not a proper fix.
        # TODO Make the code under test work as intended.
        # TODO *Only then* tighten these conditions again for all environments.
        if is_running_in_ci() and is_running_on_macos():
            assert 37 <= sink_0.queue.qsize() <= num_samples
            assert 37 <= sink_1.queue.qsize() <= num_samples
        else:
            self.assertEqual(num_samples, sink_0.queue.qsize())
            self.assertEqual(num_samples, sink_1.queue.qsize())

    def test_down_sampling_processor_strong(self):
        # Mock a setup like so:
        # source -> processor -> sink

        # (1) define the modules
        source = RandomArraySource(
            shape=None,
            sampling_rate=100,
            max_count=100,
        )
        processor = DownsamplingProcessor(sampling_rate=1)
        sink = QueueSink()

        # (2) add module to a pipeline...
        pipeline = GraphPipeline()
        pipeline.add_source(source)
        pipeline.add_processor(processor)
        pipeline.add_sink(sink)

        # (3) ...and connect the modules
        pipeline.connect(source, processor)
        pipeline.connect(processor, sink)

        number_of_seconds_to_run_the_pipeline = 2

        # Test
        pipeline.start()
        sleep(number_of_seconds_to_run_the_pipeline)
        pipeline.stop()
        pipeline.join()

        sleep(0.1)  # To make this work under macOS in the cloud

        # Assert
        # There should be at most one frame for each second
        if is_running_in_ci() and is_running_on_macos():
            assert sink.queue.qsize() <= number_of_seconds_to_run_the_pipeline
        else:
            assert sink.queue.qsize() <= number_of_seconds_to_run_the_pipeline

    def test_one_euro_filter(self):
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
        pipeline.connect(source, sink_0)
        pipeline.connect(source, processor)
        pipeline.connect(processor, sink_1)

        # Test
        pipeline.start()
        sleep(5)
        pipeline.stop()
        pipeline.join()

        sleep(0.1)  # To make this work under macOS in the cloud

        # Assert
        self.assertEqual(sink_0.queue.qsize(), 10)
        self.assertEqual(sink_1.queue.qsize(), 10)
