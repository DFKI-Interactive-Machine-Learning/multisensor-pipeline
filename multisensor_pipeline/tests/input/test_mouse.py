from time import sleep


def test_simple_mouse(xvfb):
    from multisensor_pipeline.modules import QueueSink
    from multisensor_pipeline.modules.input.mouse import Mouse
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
