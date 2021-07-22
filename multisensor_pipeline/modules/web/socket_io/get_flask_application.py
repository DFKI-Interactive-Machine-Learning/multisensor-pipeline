from flask import Flask

from multisensor_pipeline.tests.paths import DATA_WEB_PATH


def get_flask_application() -> Flask:
    flask_application: Flask = \
        Flask(
            import_name=__name__,
            template_folder=DATA_WEB_PATH,
            static_folder=DATA_WEB_PATH,
        )

    return flask_application
