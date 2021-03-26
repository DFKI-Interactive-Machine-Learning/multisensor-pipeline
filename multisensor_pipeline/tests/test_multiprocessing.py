from unittest import TestCase
from multisensor_pipeline.experimental.multiprocess import MultiprocessSourceWrapper, MultiprocessSinkWrapper, \
    MultiprocessProcessorWrapper
from multisensor_pipeline.modules.npy import RandomArraySource, ArrayManipulationProcessor
from multisensor_pipeline.modules.console import ConsoleSink
from multisensor_pipeline.modules import PassthroughProcessor, QueueSink
from multisensor_pipeline.pipeline import GraphPipeline
import numpy as np
import time
import logging


logging.basicConfig(level=logging.DEBUG)


class PipelineTest(TestCase):

    def setUp(self) -> None:
        pass

    def test_source_sink_wrapper(self):
        # create nodes
        source = MultiprocessSourceWrapper(module_cls=RandomArraySource, shape=(5,), frequency=.001)
        sink = MultiprocessSinkWrapper(module_cls=ConsoleSink)
        #queue = QueueSink()

        # connect nodes
        source.add_observer(sink)
        #source.add_observer(queue)

        # start nodes
        sink.start()
        #queue.start()
        source.start()

        time.sleep(3)

        source.stop(blocking=False)
        sink.join()
        #queue.join()

        #self.assertFalse(queue.empty())

    def test_processor_wrapper(self):
        # create nodes
        source = MultiprocessSourceWrapper(module_cls=RandomArraySource, shape=(50,), frequency=50)
        processor = MultiprocessProcessorWrapper(module_cls=ArrayManipulationProcessor, numpy_operation=np.mean)
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

        time.sleep(.5)

        # sink.stop()
        # processor.stop()
        source.stop()
        sink.join()
        queue.join()

        self.assertFalse(queue.empty())

    def test_parallelized_pipeline(self):
        # create modules
        source = MultiprocessSourceWrapper(module_cls=RandomArraySource, shape=(50,), frequency=50)
        processor1 = PassthroughProcessor()
        processor2 = MultiprocessProcessorWrapper(module_cls=ArrayManipulationProcessor, numpy_operation=np.mean)
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
        time.sleep(.1)
        pipeline.stop()

        self.assertFalse(queue.empty())
