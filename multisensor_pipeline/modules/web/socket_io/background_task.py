from typing import Optional

from flask_socketio import SocketIO


def background_task(
    *,
    socket_io: SocketIO,
    namespace: Optional[str] = None,
):
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socket_io.sleep(10)
        count += 1
        socket_io.emit(
            'response',
            {
                'data': 'Server generated event',
                'count': count,
            },
            namespace=namespace,
        )
