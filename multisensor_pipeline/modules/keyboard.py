import collections

from pynput import  keyboard
from multisensor_pipeline.modules.base import BaseSource
from multisensor_pipeline.dataframe import  MSPDataFrame, Topic
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class KeyboardSource(BaseSource):
    """
    Source for keyboard input. Can observe keyboard press and releases of button
    """

    def __init__(self, press=True, release=False):
        super().__init__()
        self.press = press
        self.release = release
        self.stop_listener = False
        self.listener = None
        self.queue = collections.deque()
        self._keypress_topic = Topic(name="keyboard.press", dtype=str)
        self._keyrelease_topic = Topic(name="keyboard.release", dtype=str)

    def on_start(self):
        args = {}
        if self.press:
            args["on_press"] = self.on_press
        if self.release:
            args["on_release"] = self.on_release

        self.listener = keyboard.Listener(**args)
        self.listener.start()

    def on_press(self, key):
        frame = MSPDataFrame(topic=self._keypress_topic, data=key)
        self.queue.append(frame)

    def on_release(self, key):
        frame = MSPDataFrame(topic=self._keyrelease_topic, data=key)
        self.queue.append(frame)

    def on_update(self) -> Optional[MSPDataFrame]:
        while not self.queue:
            if self.stop_listener:
                return
        return self.queue.popleft()

    def on_stop(self):
        self.stop_listener = True
        self.listener.stop()

    @property
    def output_topics(self) -> Optional[List[Topic]]:
        return [self._keyrelease_topic, self._keypress_topic]


