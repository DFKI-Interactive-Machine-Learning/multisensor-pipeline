from queue import Queue
from time import sleep
from typing import Tuple

from multisensor_pipeline.dataframe.dataframe import Topic

from multisensor_pipeline.dataframe import MSPDataFrame
from multisensor_pipeline.modules import QueueSink
from multisensor_pipeline.modules.web.msp.float_loop_source import \
    FloatLoopSource
from multisensor_pipeline.modules.web.msp.processor import WebProcessor
from multisensor_pipeline.pipeline.graph import GraphPipeline


def test_source_web_sink(client):
    # Mock a setup like so:
    # float_loop_source -> web_processor -> queue_sink

    floats: Tuple[float, float] = (0.9, 0.1)
    float_loop_source: FloatLoopSource = \
        FloatLoopSource(sampling_rate=1., floats=floats)
    web_processor: WebProcessor = WebProcessor()
    queue_sink: QueueSink = QueueSink()

    pipeline = GraphPipeline()
    pipeline.add_source(float_loop_source)
    pipeline.add_processor(web_processor)
    pipeline.add_sink(queue_sink)

    pipeline.connect(float_loop_source, web_processor)
    pipeline.connect(web_processor, queue_sink)

    pipeline_runtime: int = 1

    # Test
    pipeline.start()
    sleep(pipeline_runtime)
    pipeline.stop()
    pipeline.join()

    # Assert
    assert queue_sink.queue is not None
    assert isinstance(queue_sink.queue, Queue)
    assert not queue_sink.queue.empty()
    assert 0 < queue_sink.queue.qsize() <= \
           pipeline_runtime + 1

    while not queue_sink.queue.empty():
        data: MSPDataFrame = queue_sink.queue.get(timeout=0.1)
        assert data is not None
        assert isinstance(data, MSPDataFrame)
        assert data.topic is not None
        assert isinstance(data.topic, Topic)
        assert data.timestamp is not None
        assert isinstance(data.timestamp, float)
        assert data['value'] is not None
        assert isinstance(data['value'], float)
        assert data['value'] in floats
