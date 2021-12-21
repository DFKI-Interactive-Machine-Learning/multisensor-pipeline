import unittest
from time import sleep
import pynput
from pynput.keyboard import Controller, Key
from multisensor_pipeline.modules import QueueSink, ListSink
from multisensor_pipeline.modules.keyboard import KeyboardSource
from multisensor_pipeline.modules.mouse import Mouse
from multisensor_pipeline.pipeline.graph import GraphPipeline


class KeyboardTests(unittest.TestCase):

    def test_keyboard_simple(self):
        # Mock
        # (1) define the modules
        source = KeyboardSource(press=True, release=True)
        sink = QueueSink()

        # (2) add module to a pipeline...
        pipeline = GraphPipeline()
        pipeline.add_source(source)
        pipeline.add_sink(sink)

        # (3) ...and connect the modules
        pipeline.connect(source, sink)

        # Test
        pipeline.start()
        sleep(.3)
        pipeline.stop()

    def test_keyboard_simulated(self):
        # Mock
        # (1) define the modules
        keyboard = Controller()
        source = KeyboardSource(press=True, release=True)
        sink = ListSink()

        # (2) add module to a pipeline...
        pipeline = GraphPipeline()
        pipeline.add_source(source)
        pipeline.add_sink(sink)

        # (3) ...and connect the modules
        pipeline.connect(source, sink)

        # Test
        pipeline.start()
        keyboard.press(Key.ctrl)
        keyboard.release(Key.ctrl)
        sleep(.3)
        pipeline.stop()

        # Assert
        expected_events = 2
        self.assertEqual(len(sink), expected_events, "number of keyboard interactions are not correctly recognized or "
                                                     "permission to simulate a keyboard is not given ")

    def test_keyboard_topic(self):
        # Mock
        # (1) define the modules
        keyboard = Controller()
        source = KeyboardSource(press=True, release=True)
        sink = ListSink()

        # (2) add module to a pipeline...
        pipeline = GraphPipeline()
        pipeline.add_source(source)
        pipeline.add_sink(sink)

        # (3) ...and connect the modules
        pipeline.connect(source, sink, topics=source.output_topics[0])

        # Test
        pipeline.start()
        keyboard.press(Key.ctrl)
        keyboard.release(Key.ctrl)
        sleep(.3)
        pipeline.stop()

        # Assert
        expected_events = 1
        self.assertEqual(len(sink), expected_events, "number of keyboard interactions are not correctly recognized or "
                                                     "permission to simulate a keyboard is not given ")


class MouseTests(unittest.TestCase):

    def test_mouse_simple(self):
        # (1) define the modules
        source = Mouse(move=True, scroll=True, click=True)
        sink: QueueSink = QueueSink()

        # (2) add module to a pipeline...
        pipeline = GraphPipeline()
        pipeline.add_source(source)
        pipeline.add_sink(sink)

        # (3) ...and connect the modules
        pipeline.connect(source, sink)

        # Test
        pipeline.start()
        sleep(.3)
        pipeline.stop()

    def test_simulated_mouse(self):
        # (1) define the modules
        source = Mouse(move=True, scroll=True, click=True)
        sink = ListSink()

        # (2) add module to a pipeline...
        pipeline = GraphPipeline()
        pipeline.add_source(source)
        pipeline.add_sink(sink)

        # (3) ...and connect the modules
        pipeline.connect(source, sink)

        controller = pynput.mouse.Controller()
        # Test
        pipeline.start()
        controller.release(pynput.mouse.Button.middle)
        sleep(.3)
        pipeline.stop()

        expected_events = 1
        release_count = 0
        for elements in sink.list:
            if elements.topic == source.output_topics[1]:
                release_count += 1
        self.assertEqual(release_count, expected_events, "number of mouse interactions are not correctly recognized "
                                                         "or permission to simulate a keyboard is not given")


    def test_simulated_mouse_topic(self):
        # (1) define the modules
        source = Mouse(move=True, scroll=True, click=True)
        sink = ListSink()

        # (2) add module to a pipeline...
        pipeline = GraphPipeline()
        pipeline.add_source(source)
        pipeline.add_sink(sink)

        # (3) ...and connect the modules
        pipeline.connect(source, sink, topics=source.output_topics[1])

        controller = pynput.mouse.Controller()
        # Test
        pipeline.start()
        controller.release(pynput.mouse.Button.middle)
        sleep(.3)
        pipeline.stop()

        expected_events = 1
        self.assertEqual(len(sink), expected_events, "number of mouse interactions are not correctly recognized or "
                                                     "permission to simulate a keyboard is not given")
