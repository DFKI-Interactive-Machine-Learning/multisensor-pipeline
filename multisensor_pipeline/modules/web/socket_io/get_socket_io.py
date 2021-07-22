from flask import Flask
from flask_socketio import SocketIO

from multisensor_pipeline.modules.web.socket_io.configuration import \
    SOCKET_IO_ASYNC_MODE


def get_socket_io(app: Flask) -> SocketIO:
    socket_io: SocketIO = SocketIO(
        logger=True,
        engineio_logger=True,
        app=app,
        async_mode=SOCKET_IO_ASYNC_MODE,
    )

    return socket_io
