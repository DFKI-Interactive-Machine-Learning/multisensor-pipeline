from functools import partial
from multiprocessing import Process
from time import sleep
from uuid import uuid4

from multisensor_pipeline import BaseProcessor
from multisensor_pipeline.dataframe.dataframe import MSPDataFrame, Topic
from typing import Optional
import logging

from multisensor_pipeline.modules.web.socket_io.get_connections import \
    get_connections
from multisensor_pipeline.modules.web.socket_io.run_app import _main

logger = logging.getLogger(__name__)


class WebProcessor(BaseProcessor):

    def __init__(self):
        """Exchange frame data between an MSP pipeline and a web interface."""
        super(WebProcessor, self).__init__()

        server_to_client_connection_read, server_to_client_connection_write = \
            get_connections()

        _main_partial = partial(
            _main,
            server_to_client_connection_read=server_to_client_connection_read,
            server_to_client_connection_write=server_to_client_connection_write,  # TODO
        )
        self._webserver_process: Process = Process(
            target=_main_partial,
        )
        self._webserver_process.start()

        self.server_to_client_connection_read = \
            server_to_client_connection_read
        self.server_to_client_connection_write = \
            server_to_client_connection_write

    def on_update(self, frame: MSPDataFrame) -> Optional[MSPDataFrame]:

        self.server_to_client_connection_write.send(
            obj={'my_key': 'my_value'},
        )

        server_frame = frame

        client_frame: Optional[MSPDataFrame] = \
            self._on_update(server_frame=server_frame)

        return client_frame

    def _on_update(self, server_frame) -> Optional[MSPDataFrame]:
        # TODO Get data from client

        client_frame = server_frame  # TODO delete me

        return client_frame

    def on_stop(self):
        self._webserver_process.terminate()


if __name__ == '__main__':
    web_processor: WebProcessor = WebProcessor()
    topic: Topic = Topic(
        source_uuid=str(uuid4()),
        name="my_dataframe_topic",
    )
    frame: MSPDataFrame = MSPDataFrame(
        topic=topic,
        value='my_dataframe_value'
    )
    web_processor.on_update(frame=frame)
    sleep(5)
    web_processor.on_update(frame=frame)
    sleep(5)
    web_processor.on_update(frame=frame)
    sleep(5)
    web_processor.on_update(frame=frame)
