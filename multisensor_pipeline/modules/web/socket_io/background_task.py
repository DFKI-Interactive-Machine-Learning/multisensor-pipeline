import json
from multiprocessing.connection import Connection

from flask_socketio import SocketIO


def background_task(
    *,
    socket_io: SocketIO,
    server_to_client_connection_read: Connection,
):
    """Send server generated events to clients."""

    while True:
        # If there is no data to be send to client, try again in a bit.
        if not server_to_client_connection_read.poll():
            socket_io.sleep(.1)
            continue

        server_sent_data: object = server_to_client_connection_read.recv()

        print('Sending server data:', json.dumps(server_sent_data))
        socket_io.emit(
            'response',
            {
                'data': json.dumps(server_sent_data),
            },
        )
