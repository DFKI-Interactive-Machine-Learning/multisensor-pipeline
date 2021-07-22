from multisensor_pipeline import BaseProcessor
from multisensor_pipeline.dataframe.dataframe import MSPDataFrame
from typing import Optional
import logging


logger = logging.getLogger(__name__)


class WebProcessor(BaseProcessor):

    def __init__(self):
        """Exchange frame data between an MSP pipeline and a web interface."""
        super(WebProcessor, self).__init__()

    def on_update(self, frame: MSPDataFrame) -> Optional[MSPDataFrame]:

        server_frame = frame

        client_frame: Optional[MSPDataFrame] = \
            self._on_update(server_frame=server_frame)

        return client_frame

    def _on_update(self, server_frame) -> Optional[MSPDataFrame]:
        # TODO Send data to client

        # TODO Get data from client

        client_frame = server_frame  # TODO delete me

        return client_frame
