from multisensor_pipeline.modules.web.socket_io.create_app_and_socket_io \
    import create_app_and_socket_io
from multisensor_pipeline.modules.web.socket_io.datetime_namespace import \
    DatetimeNamespace
from multisensor_pipeline.modules.web.socket_io.get_datetime_namespace import \
    get_datetime_namespace

if __name__ == '__main__':
    app, socket_io = create_app_and_socket_io()

    datetime_namespace: DatetimeNamespace = \
        get_datetime_namespace(socket_io=socket_io)
    socket_io.on_namespace(namespace_handler=datetime_namespace)

    host = '0.0.0.0'
    port = 5000
    debug = True

    socket_io.run(
        app=app,
        host=host,
        port=port,
        debug=debug,
    )
