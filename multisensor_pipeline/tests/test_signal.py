from time import sleep

from multisensor_pipeline.modules import QueueSink
from multisensor_pipeline.modules.npy import RandomArraySource
from multisensor_pipeline.modules.signal.filtering import OneEuroProcessor
from multisensor_pipeline.modules.signal.sampling import DownsamplingProcessor
from multisensor_pipeline.pipeline.graph import GraphPipeline


def test_down_sampling_processor_no_downsampling():
    # Mock a setup like so:
    # sink_0 <- source -> processor -> sink_1

    # (1) define the modules
    source = RandomArraySource(
        shape=None,
        sampling_rate=100,
        max_count=100,
    )
    processor = DownsamplingProcessor(sampling_rate=150)
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
    sleep(2)
    pipeline.stop()

    # Assert
    assert not sink_0.queue.empty()
    assert sink_0.queue.qsize() > 10
    assert not sink_1.queue.empty()
    assert sink_1.queue.qsize() > 10
    # The sink connected more directly to the source may be longer.
    assert sink_0.queue.qsize() >= sink_1.queue.qsize()


def test_down_sampling_processor_strong():
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
    assert sink.queue.qsize() <= 2


def test_one_euro_filter():
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
    assert sink.queue.qsize() <= sink2.queue.qsize()
