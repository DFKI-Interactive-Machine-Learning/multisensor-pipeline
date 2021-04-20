import collections
from time import sleep
from pynput import  keyboard
from multisensor_pipeline import GraphPipeline
from multisensor_pipeline.modules import ConsoleSink
from multisensor_pipeline.modules.base import BaseSource
from multisensor_pipeline.dataframe import  MSPDataFrame
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class Keyboard(BaseSource):
    """Source for keyboard input. Can observe keyboard press and releases of button
    """

    def __init__(self, press=True, release=False):
        super().__init__()
        self.press = press
        self.release = release
        self.stop_listener = False
        self.listener = None
        self.queue = collections.deque()

    def on_start(self):
        args = {}
        if self.press:
            args["on_press"] = self.on_press
        if self.release:
            args["on_release"] = self.on_release

        self.listener = keyboard.Listener(**args)
        self.listener.start()

    def on_press(self, key):
        frame = MSPDataFrame(topic=self._generate_topic(name="mouse.coordinates", dtype=str), chunk={"key": key})
        self.queue.append(frame)

    def on_release(self, key):
        frame = MSPDataFrame(topic=self._generate_topic(name="mouse.coordinates", dtype=str), chunk={"key": key})

    def on_update(self) -> Optional[MSPDataFrame]:
        while not self.queue:
            if self.stop_listener:
                return
        return self.queue.popleft()

    def on_stop(self):
        self.stop_listener = True
        self.listener.stop()


if __name__ == '__main__':
    # (1) define the modules
    source = Keyboard(press=True, release=True)
    sink = ConsoleSink()

    # (2) add module to a pipeline...
    pipeline = GraphPipeline()
    pipeline.add_source(source)
    pipeline.add_sink(sink)
    # (3) ...and connect the modules
    pipeline.connect(source, sink)

    # (4) print mouse movements
    pipeline.start()
    sleep(5)
    pipeline.stop()
