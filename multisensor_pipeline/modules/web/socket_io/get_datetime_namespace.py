from multiprocessing.connection import Connection

from multisensor_pipeline.modules.web.socket_io.datetime_namespace import \
    DatetimeNamespace


def get_datetime_namespace(
    *,
    socket_io,
    server_to_client_connection_write: Connection,
    server_to_client_connection_read: Connection,
) -> DatetimeNamespace:
    namespace = '/'

    datetime_namespace: DatetimeNamespace = \
        DatetimeNamespace(
            namespace=namespace,
            socket_io=socket_io,
            server_to_client_connection_read=server_to_client_connection_read,
            server_to_client_connection_write=server_to_client_connection_write,
        )

    return datetime_namespace
