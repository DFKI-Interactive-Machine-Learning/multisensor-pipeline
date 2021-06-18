from time import sleep

import pytest

from multisensor_pipeline.tests.environment_properties import \
    is_running_on_windows


@pytest.mark.skipif(
    # TODO Deactivating a test just like that is not a proper fix.
    # TODO Add an equivalent test that works under Windows.
    # TODO Keep this one for macOS and Linux.
    is_running_on_windows(),
    reason="Does not run on Windows.",
)
@pytest.mark.timeout(0.320 * 10)  # Kill runs taking 10x longer than local
def test_simple_mouse(xvfb):
    from multisensor_pipeline.modules import QueueSink
    from multisensor_pipeline.modules.mouse import Mouse
    from multisensor_pipeline.pipeline.graph import GraphPipeline

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

    # Assert
    # If we ever get here, we consider this test successful.
    assert True


@pytest.mark.skipif(
    # TODO Deactivating a test just like that is not a proper fix.
    # TODO Add an equivalent test that works under Windows.
    # TODO Keep this one for macOS and Linux.
    is_running_on_windows(),
    reason="Does not run on Windows.",
)
@pytest.mark.timeout(0.420 * 10)  # Kill runs taking 10x longer than local
def test_simple_keyboard(xvfb):
    from multisensor_pipeline.modules import QueueSink
    from multisensor_pipeline.modules.keyboard import Keyboard
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


@pytest.mark.skipif(
    # TODO Deactivating a test just like that is not a proper fix.
    # TODO Add an equivalent test that works under Windows.
    # TODO Keep this one for macOS and Linux.
    is_running_on_windows(),
    reason="Does not run on Windows.",
)
def _test_simulated_keyboard_input(xvfb):
    from multisensor_pipeline.modules import ListSink
    from multisensor_pipeline.modules.keyboard import Keyboard
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
        # There seems te be a bug in pynput keyboard controller for macOS:
        # Keypress is recognized as press and release
        expected_events *= 2
    assert len(sink.list) == expected_events, \
        "number of keyboard interactions are not correctly recognized or permission to simulate a keyboard is not given"
