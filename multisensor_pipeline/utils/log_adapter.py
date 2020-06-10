from kivy.logger import Logger
import logging


class KivyLogAdapter(logging.Handler):

    def __init__(self, level=logging.NOTSET):
        super().__init__(level=level)

    def emit(self, record):
        Logger.info(f"{record.name}: {record.msg}")

    @staticmethod
    def bind_logger(name, level=logging.INFO):
        Logger.info(f"{KivyLogAdapter.__name__}: binding {name}")
        log = logging.getLogger(name)
        log.setLevel(level)
        log.addHandler(KivyLogAdapter(level))
