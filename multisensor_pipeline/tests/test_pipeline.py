from time import sleep

from pytest import fixture, raises

from multisensor_pipeline.modules.base.base import BaseSource, BaseSink
from multisensor_pipeline.pipeline.graph import GraphPipeline


@fixture
def pipeline():
    pipeline: GraphPipeline = GraphPipeline()

    return pipeline


class SourceModule(BaseSource):
    pass


class SinkModule(BaseSink):
    pass


def test_pipeline(pipeline):
    # Mock
    source_module: SourceModule = SourceModule()
    sink_module: SinkModule = SinkModule()
    pipeline.add(modules=[source_module, sink_module])
    pipeline.connect(module=source_module, successor=sink_module)

    # Test
    with pipeline:
        sleep(0.001)

    # Assert
    assert True  # If we get here, we consider that a success


def test_pipeline_manual_start(pipeline):
    # Mock
    source_module: SourceModule = SourceModule()
    sink_module: SinkModule = SinkModule()
    pipeline.add(modules=[source_module, sink_module])
    pipeline.connect(module=source_module, successor=sink_module)

    # Test
    with raises(expected_exception=RuntimeError):
        with pipeline:
            pipeline.start()

            sleep(0.001)

    # Assert
    assert True  # If we get here, we consider that a success


def test_pipeline_manual_stop(pipeline):
    # Mock
    source_module: SourceModule = SourceModule()
    sink_module: SinkModule = SinkModule()
    pipeline.add(modules=[source_module, sink_module])
    pipeline.connect(module=source_module, successor=sink_module)

    # Test
    with pipeline:
        sleep(0.001)

    pipeline.stop()

    # Assert
    assert True  # If we get here, we consider that a success


def test_pipeline_manual_stop_and_join(pipeline):
    # Mock
    source_module: SourceModule = SourceModule()
    sink_module: SinkModule = SinkModule()
    pipeline.add(modules=[source_module, sink_module])
    pipeline.connect(module=source_module, successor=sink_module)

    # Test
    with pipeline:
        sleep(0.001)

    pipeline.stop()
    pipeline.join()

    # Assert
    assert True  # If we get here, we consider that a success


def test_pipeline_manual_join(pipeline):
    # Mock
    source_module: SourceModule = SourceModule()
    sink_module: SinkModule = SinkModule()
    pipeline.add(modules=[source_module, sink_module])
    pipeline.connect(module=source_module, successor=sink_module)

    # Test
    with pipeline:
        sleep(0.001)

    pipeline.join()

    # Assert
    assert True  # If we get here, we consider that a success
