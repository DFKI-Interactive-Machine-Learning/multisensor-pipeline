from time import sleep

from multisensor_pipeline.modules import QueueSink
from multisensor_pipeline.modules.npy import RandomArraySource
from multisensor_pipeline.modules.signal.sampling import DownsamplingProcessor
from multisensor_pipeline.pipeline.graph import GraphPipeline


def test_down_sampling_processor_strong():
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

    # Test
    pipeline.start()
    sleep(1)
    pipeline.stop()

    # Assert
    assert sink.queue.qsize() <= 3
