from socket import SocketIO

import pytest
from flask import Flask

from multisensor_pipeline.modules.web.socket_io.create_app_and_socket_io \
    import create_app_and_socket_io


@pytest.fixture
def client():
    app, socket_io = create_app_and_socket_io()
    app: Flask
    socket_io: SocketIO

    with app.test_client() as client:
        yield client
