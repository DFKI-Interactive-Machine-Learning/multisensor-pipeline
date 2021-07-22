from multiprocessing import Pipe
from multiprocessing.connection import Connection
from typing import Tuple


def get_connections() -> Tuple[Connection, Connection]:
    server_to_client_connection_read: Connection
    server_to_client_connection_write: Connection

    server_to_client_connection_read, server_to_client_connection_write = \
        Pipe(duplex=False)

    return server_to_client_connection_read, server_to_client_connection_write
