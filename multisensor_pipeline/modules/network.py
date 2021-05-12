from typing import Optional
import zmq
import logging
import json

from multisensor_pipeline.dataframe.dataframe import MSPDataFrame
from multisensor_pipeline.modules import BaseSink
from multisensor_pipeline.modules.base.base import BaseSource

logger = logging.getLogger(__name__)


class ZmqPublisher(BaseSink):

    def __init__(self, protocol='tcp', url='*', port=5000):
        super(ZmqPublisher, self).__init__()

        self.protocol = protocol
        self.url = url
        self.port = port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind(
            "{}://{}:{}".format(self.protocol, self.url, self.port)
        )

    def on_update(self, frame: MSPDataFrame):
        # payload = (frame.topic.name, msgpack.packb(frame, use_bin_type=True))
        # self.socket.send_multipart(payload)
        payload = json.dumps(frame, cls=MSPDataFrame.JsonEncoder)
        self.socket.send_json(payload)

    def on_stop(self):
        self.socket.close()
        self.context.term()


class ZmqSubscriber(BaseSource):

    def __init__(
        self,
        topic_filter='',
        protocol='tcp',
        url='127.0.0.1',
        port=5000,
    ):
        super(ZmqSubscriber, self).__init__()

        self.protocol = protocol
        self.url = url
        self.port = port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect(
            "{}://{}:{}".format(self.protocol, self.url, self.port)
        )

        self.source_filter = topic_filter
        self.socket.setsockopt_string(zmq.SUBSCRIBE, self.source_filter)

    def on_update(self) -> Optional[MSPDataFrame]:
        payload = self.socket.recv_json()
        frame = MSPDataFrame(
            **json.loads(s=payload, cls=MSPDataFrame.JsonDecoder),
        )
        return frame

    def on_stop(self):
        self.socket.close()
        self.context.term()
