import time
import logging

import numpy as np

from multisensor_pipeline.modules.multiprocess import \
    MultiprocessSourceWrapper, MultiprocessSinkWrapper, \
    MultiprocessProcessorWrapper
from multisensor_pipeline.modules.npy import RandomArraySource, \
    ArrayManipulationProcessor
from multisensor_pipeline.modules import PassthroughProcessor, QueueSink, \
    ConsoleSink
from multisensor_pipeline.pipeline.graph import GraphPipeline

logging.basicConfig(level=logging.DEBUG)


def test_source_sink_wrapper():
    # create nodes
    source = MultiprocessSourceWrapper(
        module_cls=RandomArraySource,
        shape=(5,),
        sampling_rate=50,
    )
    sink = MultiprocessSinkWrapper(module_cls=ConsoleSink)
    queue = QueueSink()

    # connect nodes
    source.add_observer(sink)
    source.add_observer(queue)

    # start nodes
    sink.start()
    queue.start()
    source.start()

    time.sleep(.5)

    source.stop(blocking=False)
    sink.join()

    assert not source._process.is_alive()
    assert not source._thread.is_alive()
    assert not sink._process.is_alive()
    assert not sink._thread.is_alive()

    queue.join()

    assert not queue.empty()


def test_processor_wrapper():
    # create nodes
    source = MultiprocessSourceWrapper(
        module_cls=RandomArraySource,
        shape=(50,),
        sampling_rate=50,
    )
    processor = MultiprocessProcessorWrapper(
        module_cls=ArrayManipulationProcessor,
        numpy_operation=np.mean,
    )
    sink = MultiprocessSinkWrapper(module_cls=ConsoleSink)
    queue = QueueSink()

    # connect nodes
    source.add_observer(processor)
    processor.add_observer(sink)
    processor.add_observer(queue)

    # start nodes
    sink.start()
    queue.start()
    processor.start()
    source.start()

    time.sleep(.25)

    source.stop()
    sink.join()
    queue.join()

    assert not queue.empty()


def test_parallelized_pipeline():
    # create modules
    source = MultiprocessSourceWrapper(
        module_cls=RandomArraySource,
        shape=(50,),
        sampling_rate=50,
    )
    processor1 = PassthroughProcessor()
    processor2 = MultiprocessProcessorWrapper(
        module_cls=ArrayManipulationProcessor,
        numpy_operation=np.mean,
    )
    queue = QueueSink()

    # add modules to a pipeline
    pipeline = GraphPipeline()
    pipeline.add_source(source)
    pipeline.add_processor(processor1)
    pipeline.add_processor(processor2)
    pipeline.add_sink(queue)

    # connect modules
    pipeline.connect(source, processor1)
    pipeline.connect(processor1, processor2)
    pipeline.connect(processor2, queue)

    pipeline.start()
    time.sleep(.25)
    pipeline.stop()

    assert not queue.empty()
