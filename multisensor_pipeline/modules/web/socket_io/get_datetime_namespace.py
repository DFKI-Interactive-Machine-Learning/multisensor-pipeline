from multisensor_pipeline.modules.web.socket_io.datetime_namespace import \
    DatetimeNamespace


def get_datetime_namespace(socket_io) -> DatetimeNamespace:
    namespace = '/'

    datetime_namespace: DatetimeNamespace = \
        DatetimeNamespace(
            namespace=namespace,
            socket_io=socket_io,
        )

    return datetime_namespace
