import collections
from typing import Optional
import logging

from pynput import mouse

from multisensor_pipeline.dataframe.dataframe import MSPEventFrame, \
    MSPDataFrame
from multisensor_pipeline.modules.base.base import BaseSource

logger = logging.getLogger(__name__)


class Mouse(BaseSource):
    """
    Source for mouse input.

    Can observe mouse movement, scroll and clicks.
    Sends MSPEventFrame when mouse changes are detected
    """

    def __init__(self, move=True, click=False, scroll=False):
        super().__init__()
        self.move = move
        self.click = click
        self.scroll = scroll
        self.stop_listener = False
        self.listener = None
        self.queue = collections.deque()

    def on_start(self):
        args = {}
        if self.move:
            args["on_move"] = self.on_move
        if self.click:
            args["on_click"] = self.on_click
        if self.scroll:
            args["on_scroll"] = self.on_scroll

        self.listener = mouse.Listener(**args)
        self.listener.start()

    def on_move(self, x, y):
        frame = MSPEventFrame(
            topic=self._generate_topic(name="mouse.coordinates", dtype=float),
            chunk={"x": x, "y": y},
        )
        self.queue.append(frame)

    def on_click(self, x, y, button, pressed):
        frame = MSPEventFrame(
            topic=self._generate_topic(name="mouse.click", dtype=float),
            chunk={"x": x, "y": y, "button": button, "pressed": pressed},
        )
        self.queue.append(frame)

    def on_scroll(self, x, y, dx, dy):
        frame = MSPEventFrame(
            topic=self._generate_topic(name="mouse.scroll", dtype=float),
            chunk={"x": x, "y": y, "scroll_x": dx, "scroll_y": dy},
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
