from multisensor_pipeline.modules.base import BaseSink, BaseSource
from ..utils.dataframe import MSPDataFrame
import zmq
import logging
import msgpack

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

    def _update(self, frame=None):
        while self._active:
            dtype, data = self.get()
            payload = (dtype, msgpack.packb(data, use_bin_type=True))
            self.socket.send_multipart(payload)

    def _stop(self):
        self.socket.close()
        self.context.term()


class ZmqSubscriber(BaseSource):

    def __init__(self, source_filter='', protocol='tcp', url='127.0.0.1', port=5000):
        super(ZmqSubscriber, self).__init__()

        self.protocol = protocol
        self.url = url
        self.port = port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect("{}://{}:{}".format(self.protocol, self.url, self.port))

        self.source_filter = source_filter
        self.socket.setsockopt_string(zmq.SUBSCRIBE, self.source_filter)

    def _update(self, frame=None):
        while self._active:
            packet = self.socket.recv_multipart()
            dtype = packet[0]
            data = msgpack.unpackb(packet[1], raw=False)
            data = MSPDataFrame(init_dict=data)
            self._notify_all(dtype, data)

    def _stop(self):
        self.socket.close()
        self.context.term()
