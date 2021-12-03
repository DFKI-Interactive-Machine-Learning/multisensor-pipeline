from multisensor_pipeline.modules.base import BaseSink, BaseSource
from multisensor_pipeline.dataframe.dataframe import MSPDataFrame, Topic
from typing import Optional, List
import zmq
import logging
import json

logger = logging.getLogger(__name__)


class ZmqPublisher(BaseSink):

    def __init__(self, protocol='tcp', url='*', port=5000):
        super(ZmqPublisher, self).__init__()

        self.protocol = protocol
        self.url = url
        self.port = port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind("{}://{}:{}".format(self.protocol, self.url, self.port))

    def on_update(self, frame: MSPDataFrame):
        payload = json.dumps(frame, cls=MSPDataFrame.JsonEncoder)
        self.socket.send_json(payload)

    def on_stop(self):
        self.socket.close()
        self.context.term()

    @property
    def input_topics(self) -> List[Topic]:
        return [Topic()]


class ZmqSubscriber(BaseSource):

    def __init__(self, topic_filter='', protocol='tcp', url='127.0.0.1', port=5000):
        super(ZmqSubscriber, self).__init__()

        self.protocol = protocol
        self.url = url
        self.port = port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect("{}://{}:{}".format(self.protocol, self.url, self.port))

        self.source_filter = topic_filter
        self.socket.setsockopt_string(zmq.SUBSCRIBE, self.source_filter)

    def on_update(self) -> Optional[MSPDataFrame]:
        payload = self.socket.recv_json()
        frame = MSPDataFrame(**json.loads(s=payload, cls=MSPDataFrame.JsonDecoder))
        return frame

    def on_stop(self):
        self.socket.close()
        self.context.term()

    @property
    def output_topics(self) -> Optional[List[Topic]]:
        return [Topic()]

