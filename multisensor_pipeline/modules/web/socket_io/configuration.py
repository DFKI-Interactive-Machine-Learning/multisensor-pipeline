from typing import Optional

from flask import Flask

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
from flask_socketio import SocketIO

SOCKET_IO_ASYNC_MODE: Optional[str] = \
    SocketIO(
        app=Flask(
            import_name=__name__,
        ),
        async_mode=None,
    ).async_mode
