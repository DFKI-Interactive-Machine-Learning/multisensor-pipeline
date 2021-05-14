from time import sleep

from multisensor_pipeline.modules import QueueSink
from multisensor_pipeline.modules.npy import RandomArraySource
from multisensor_pipeline.modules.signal.filtering import OneEuroProcessor
from multisensor_pipeline.modules.signal.sampling import DownsamplingProcessor
from multisensor_pipeline.pipeline.graph import GraphPipeline


class DownsamplingProcessorTest(unittest.TestCase):
    def test_down_sampling_processor_no_downsampling(self):
        # (1) define the modules
        source = RandomArraySource(
            shape=None,
            sampling_rate=100,
            max_count=100,
        )
        processor = DownsamplingProcessor(sampling_rate=150)
        sink = QueueSink()
        sink2 = QueueSink()

        # (2) add module to a pipeline...
        pipeline = GraphPipeline()
        pipeline.add_source(source)
        pipeline.add_processor(processor)
        pipeline.add_sink(sink)
        pipeline.add_sink(sink2)
        # (3) ...and connect the modules
        pipeline.connect(source, processor)
        pipeline.connect(source, sink2)
        pipeline.connect(processor, sink)

        pipeline.start()
        sleep(2)
        pipeline.stop()
        self.assertEqual(sink.queue.qsize(), sink2.queue.qsize())

    def test_down_sampling_processor_strong(self):
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
        pipeline.start()
        sleep(1)
        pipeline.stop()
        self.assertLessEqual(sink.queue.qsize(), 2)


class OneEuroProcessorTest(unittest.TestCase):
    def test_one_euro_filter(self):
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
        sink = QueueSink()
        sink2 = QueueSink()

        # (2) add module to a pipeline...
        pipeline = GraphPipeline()
        pipeline.add_source(source)
        pipeline.add_processor(processor)
        pipeline.add_sink(sink)
        pipeline.add_sink(sink2)
        # (3) ...and connect the modules
        pipeline.connect(source, processor)
        pipeline.connect(source, sink2)
        pipeline.connect(processor, sink)

        pipeline.start()
        sleep(2)
        pipeline.stop()
        self.assertLessEqual(sink.queue.qsize(), sink2.queue.qsize())
