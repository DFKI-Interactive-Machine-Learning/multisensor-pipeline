from time import sleep

from multisensor_pipeline.modules import QueueSink
from multisensor_pipeline.modules.npy import RandomArraySource
from multisensor_pipeline.modules.signal.filtering import OneEuroProcessor
from multisensor_pipeline.pipeline.graph import GraphPipeline


def test_one_euro_filter():
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
    sleep(2)
    pipeline.stop()

    # Assert
    assert abs(sink_1.queue.qsize() - sink_0.queue.qsize()) < 2
