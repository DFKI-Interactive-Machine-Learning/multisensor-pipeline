from time import sleep


def _test_simple_keyboard(xvfb):
    from multisensor_pipeline.modules import QueueSink
    from multisensor_pipeline.modules.input.keyboard import Keyboard
    from multisensor_pipeline.pipeline.graph import GraphPipeline

    # Mock
    # (1) define the modules
    source = Keyboard(press=True, release=True)
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

    # Assert
    # If we ever get here, we consider this test successful.
    assert True


def _test_simulated_keyboard_input(xvfb):
    from multisensor_pipeline.modules import ListSink
    from multisensor_pipeline.modules.input.keyboard import Keyboard
    from multisensor_pipeline.pipeline.graph import GraphPipeline

    from pynput.keyboard import Controller, Key

    # Mock
    # (1) define the modules
    keyboard = Controller()
    source = Keyboard(press=True, release=True)
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
    if "darwin" in keyboard.__str__():
        # There seems te be a bug in pynput keyboard controller for MacOS:
        # Keypress is recognized as press and release
        expected_events *= 2
    assert \
        len(sink.list) == expected_events, \
        "number of keyboard interactions are not correctly recognized " + \
        "or permission to simulate a keyboard is not given"
