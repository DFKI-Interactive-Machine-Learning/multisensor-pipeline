from typing import Tuple

from flask import Flask
from flask_socketio import SocketIO

from multisensor_pipeline.modules.web.socket_io.blueprint import get_blueprint
from multisensor_pipeline.modules.web.socket_io.get_flask_application import \
    get_flask_application
from multisensor_pipeline.modules.web.socket_io.get_socket_io import \
    get_socket_io


def create_app_and_socket_io() -> Tuple[Flask, SocketIO]:
    flask_application: Flask = get_flask_application()

    socket_io: SocketIO = get_socket_io(app=flask_application)

    flask_application.register_blueprint(
        blueprint=get_blueprint(
            socket_io=socket_io,
        )
    )

    return flask_application, socket_io
