import collections

import typing
from pynput import mouse
from multisensor_pipeline.modules.base import BaseSource
from multisensor_pipeline.dataframe import  MSPDataFrame, Topic
from typing import Optional, List, Tuple, Dict, Generic, Any
import logging

logger = logging.getLogger(__name__)


class Mouse(BaseSource):
    """
    Source for mouse input. Can observe mouse movement, scroll and clicks.
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
        self._mouse_scroll_topic = Topic(name="mouse.scroll", dtype=Tuple[float, float])
        self._mouse_click_topic = Topic(name="mouse.click", dtype=Dict)
        self._mouse_move_topic = Topic(name="mouse.coordinates", dtype=Tuple[float,float])

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
        frame = MSPDataFrame(topic=self._mouse_move_topic, data=(x, y))
        self.queue.append(frame)

    def on_click(self, x, y, button, pressed):
        frame = MSPDataFrame(topic=self._mouse_click_topic,
                             data={"point": (x, y), "button": button, "pressed": pressed})
        self.queue.append(frame)

    def on_scroll(self, x, y, dx, dy):
        frame = MSPDataFrame(topic=self._mouse_scroll_topic,
                             data=(dx, dy))
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
        return [self._mouse_move_topic, self._mouse_click_topic, self._mouse_scroll_topic]
