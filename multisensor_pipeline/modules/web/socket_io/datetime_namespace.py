from functools import partial
from multiprocessing import Pipe
from threading import Lock

from flask import request
from flask_socketio import Namespace, emit, disconnect, SocketIO

from multisensor_pipeline.modules.web.socket_io.background_task import \
    background_task


class DatetimeNamespace(Namespace):

    _thread = None
    _thread_lock = Lock()

    def __init__(
        self,
        namespace: str,
        socket_io: SocketIO,
        server_to_client_connection_read: Pipe,
        server_to_client_connection_write: Pipe,
    ):
        super(DatetimeNamespace, self).__init__(namespace=namespace)

        self.socket_io: SocketIO = socket_io
        self.server_to_client_connection_read: Pipe = \
            server_to_client_connection_read
        self.server_to_client_connection_write: Pipe = \
            server_to_client_connection_write

    def on_event(self, message):
        emit(
            'response',
            {
                'data': message['data'],
            }
        )

    def on_broadcast_event(self, message):
        emit(
            'response',
            {
                'data': message['data'],
            },
            broadcast=True,
        )

    def on_disconnect_request(self):
        emit(
            'response',
            {
                'data': 'Disconnected!',
            },
        )
        disconnect()

    def on_ping(self):
        emit('pong')

    def on_connect(self):
        print(f'Client {request.sid} connected.')

        with DatetimeNamespace._thread_lock:
            if DatetimeNamespace._thread is None:
                background_task_partial = partial(
                    background_task,
                    socket_io=self.socket_io,
                    server_to_client_connection_read=self.
                    server_to_client_connection_read,
                )
                DatetimeNamespace._thread = \
                    self.socket_io.start_background_task(
                        target=background_task_partial,
                    )
        emit(
            'response',
            {
                'data': 'Connected',
            },
        )

    def on_disconnect(self):
        print('Client disconnected', request.sid)
