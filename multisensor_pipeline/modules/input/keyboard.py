import collections
from pynput import keyboard
from typing import Optional
import logging

from multisensor_pipeline.dataframe.dataframe import MSPEventFrame, \
    MSPDataFrame
from multisensor_pipeline.modules.base.base import BaseSource

logger = logging.getLogger(__name__)


class Keyboard(BaseSource):
    """
    Source for keyboard input.

    Can observe keyboard press and releases of button.
    """

    def __init__(self, press=True, release=False):
        super().__init__()
        self.press = press
        self.release = release
        self.stop_listener = False
        self.listener = None
        self.queue = collections.deque()

    def on_start(self):
        self.listener = keyboard.Listener(
            on_press=self.on_press if self.press else None,
            on_release=self.on_release if self.release else None,
        )
        self.listener.start()

    def on_press(self, key):
        frame = MSPEventFrame(
            topic=self._generate_topic(name="keyboard.press", dtype=str),
            chunk={"key": key},
        )
        self.queue.append(frame)

    def on_release(self, key):
        frame = MSPEventFrame(
            topic=self._generate_topic(name="keyboard.release", dtype=str),
            chunk={"key": key},
        )
        self.queue.append(frame)

    def on_update(self) -> Optional[MSPDataFrame]:
        while not self.queue:
            if self.stop_listener:
                return
        return self.queue.popleft()

    def on_stop(self):
        self.stop_listener = True
        self.listener.stop()