from socket import SocketIO

from flask import Flask

from multisensor_pipeline.modules.web.socket_io.create_app_and_socket_io \
    import create_app_and_socket_io
from multisensor_pipeline.modules.web.socket_io.datetime_namespace import \
    DatetimeNamespace
from multisensor_pipeline.modules.web.socket_io.get_connections import \
    get_connections
from multisensor_pipeline.modules.web.socket_io.get_datetime_namespace import \
    get_datetime_namespace


def main():
    server_to_client_connection_write, server_to_client_connection_read = \
        get_connections()

    _main(
        server_to_client_connection_write=server_to_client_connection_write,
        server_to_client_connection_read=server_to_client_connection_read)


def _main(server_to_client_connection_write, server_to_client_connection_read):
    app, socket_io = create_app_and_socket_io()
    app: Flask
    socket_io: SocketIO

    datetime_namespace: DatetimeNamespace = \
        get_datetime_namespace(
            socket_io=socket_io,
            server_to_client_connection_write=server_to_client_connection_write,
            server_to_client_connection_read=server_to_client_connection_read,
        )
    socket_io.on_namespace(namespace_handler=datetime_namespace)

    host: str = '0.0.0.0'
    port: int = 5000
    debug: bool = True

    socket_io.run(
        app=app,
        host=host,
        port=port,
        debug=debug,
    )


if __name__ == '__main__':
    main()
