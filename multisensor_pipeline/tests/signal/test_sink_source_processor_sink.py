from time import sleep

from multisensor_pipeline.modules import QueueSink
from multisensor_pipeline.modules.npy import RandomArraySource
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
    assert 10 <= sink_0.queue.qsize()
    assert not sink_1.queue.empty()
    assert 10 <= sink_1.queue.qsize()
    # No sink should not have received much more messages than the other
    assert abs(sink_0.queue.qsize() - sink_1.queue.qsize()) <= 3
