from multisensor_pipeline.modules.network import ZmqPublisher, ZmqSubscriber
from multisensor_pipeline.modules.npy import RandomArraySource
from multisensor_pipeline.modules import ListSink
from time import sleep
import logging

from multisensor_pipeline.pipeline.graph import GraphPipeline

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def test_zmq_pub_sub():
    wait_time = .5

    logger.info(
        "initialize pipelines: [mic -> pub] ->TCP-> [sub -> final_sink]."
    )

    # initialize subscriber pipeline
    zmq_sub = ZmqSubscriber()
    sink2 = ListSink()
    sub_pipeline = GraphPipeline()
    sub_pipeline.add_source(zmq_sub)
    sub_pipeline.add_sink(sink2)
    sub_pipeline.connect(zmq_sub, sink2)

    # initialize publisher pipeline
    pub_pipeline = GraphPipeline()
    zmq_pub = ZmqPublisher()
    sink1 = ListSink()
    source = RandomArraySource(shape=1, sampling_rate=100)
    pub_pipeline.add_source(source)
    pub_pipeline.add_sink(zmq_pub)
    pub_pipeline.add_sink(sink1)
    pub_pipeline.connect(source, zmq_pub)
    pub_pipeline.connect(source, sink1)

    logger.info("Start pipelines in forward order ...")
    pub_pipeline.start()
    sub_pipeline.start()

    logger.info("Waiting for {} seconds.".format(wait_time))
    sleep(wait_time)

    logger.info("Stopping pipelines ...")
    pub_pipeline.stop()
    pub_pipeline.join()
    sub_pipeline.stop()
    sub_pipeline.join()

    sink1_values = {
        (frame.timestamp, frame['value'].flatten().tolist()[0])
        for frame in sink1.list
    }

    sink2_values = {
        (frame.timestamp, frame['value'].flatten().tolist()[0])
        for frame in sink2.list
    }

    assert \
        len(list(sink1_values - sink2_values)) == \
        len(sink1.list) - len(sink2.list)
