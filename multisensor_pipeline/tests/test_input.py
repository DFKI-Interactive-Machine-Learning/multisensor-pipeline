import unittest
from time import sleep

from pynput.keyboard import Controller, Key

from multisensor_pipeline import GraphPipeline
from multisensor_pipeline.modules import QueueSink, ListSink
from multisensor_pipeline.modules.keyboard import Keyboard
from multisensor_pipeline.modules.mouse import Mouse


class MouseInputTest(unittest.TestCase):
    def test_simple_mouse(self):
        # (1) define the modules
        source = Mouse(move=True, scroll=True, click=True)
        sink = QueueSink()

        # (2) add module to a pipeline...
        pipeline = GraphPipeline()
        pipeline.add_source(source)
        pipeline.add_sink(sink)
        # (3) ...and connect the modules
        pipeline.connect(source, sink)

        pipeline.start()

        sleep(.3)
        pipeline.stop()
        self.assertEqual(True, True)


class KeyboardInputTest(unittest.TestCase):
    def test_simple_keyboard(self):

        # (1) define the modules
        source = Keyboard(press=True, release=True)
        sink = QueueSink()

        # (2) add module to a pipeline...
        pipeline = GraphPipeline()
        pipeline.add_source(source)
        pipeline.add_sink(sink)
        # (3) ...and connect the modules
        pipeline.connect(source, sink)

        pipeline.start()
        sleep(.3)
        pipeline.stop()
        self.assertEqual(True, True)

    def test_simulated_keyboard_input(self):

        keyboard = Controller()
        # (1) define the modules
        source = Keyboard(press=True, release=True)
        sink = ListSink()

        # (2) add module to a pipeline...
        pipeline = GraphPipeline()
        pipeline.add_source(source)
        pipeline.add_sink(sink)
        # (3) ...and connect the modules
        pipeline.connect(source, sink)

        pipeline.start()

        keyboard.press(Key.caps_lock)
        keyboard.release(Key.caps_lock)
        sleep(.3)
        pipeline.stop()
        if "darwin" in keyboard.__str__():
            # There seems te be a bug in pynput keyboard controller for Mac OSX:
            # Keypress is recognized as press and release
            self.assertEqual(4, len(sink.list), "number of keyboard interactions are not correctly recognized or "
                                                "permission to simulate a keyboard is not given")
        else:
            self.assertEqual(2, len(sink.list), "number of keyboard interactions are not correctly recognized or "
                                                "permission to simulate a keyboard is not given")
