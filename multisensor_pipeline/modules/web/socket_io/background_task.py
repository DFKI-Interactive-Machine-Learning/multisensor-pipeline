import json
from multiprocessing.connection import Connection
from typing import Optional

from flask_socketio import SocketIO


def background_task(
    *,
    socket_io: SocketIO,
    namespace: Optional[str] = None,
    server_to_client_connection_read: Connection,
):
    """Send server generated events to clients."""

    while True:

        # If there is no data to be send to client, try again in a bit.
        if not server_to_client_connection_read.poll():
            print('No data.')
            socket_io.sleep(1)
            continue
        print('Data!')

        server_sent_data: dict = server_to_client_connection_read.recv()

        print('Data:', server_sent_data)

        socket_io.emit(
            'response',
            {
                'data': json.dumps(server_sent_data),
            },
        )

        socket_io.emit(
            'response',
            {
                'data': 'Server generated event',
            },
        )
