from time import sleep


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

    pipeline.start()

    sleep(.3)
    pipeline.stop()
    assert True


def test_simple_keyboard(xvfb):
    from multisensor_pipeline.modules import QueueSink
    from multisensor_pipeline.modules.keyboard import Keyboard
    from multisensor_pipeline.pipeline.graph import GraphPipeline

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
    assert True


def test_simulated_keyboard_input(xvfb):
    from multisensor_pipeline.modules import ListSink
    from multisensor_pipeline.modules.keyboard import Keyboard
    from multisensor_pipeline.pipeline.graph import GraphPipeline

    from pynput.keyboard import Controller, Key

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
        # There seems te be a bug in pynput keyboard controller for MacOS:
        # Keypress is recognized as press and release
        assert \
            4 == len(sink.list), \
            "number of keyboard interactions are not correctly recognized " + \
            "or permission to simulate a keyboard is not given"
    else:
        assert \
            2 == len(sink.list), \
            "number of keyboard interactions are not correctly recognized " + \
            "or permission to simulate a keyboard is not given"
