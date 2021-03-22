from unittest import TestCase
from multisensor_pipeline.modules.multiprocess import MultiprocessSourceWrapper, MultiprocessSinkWrapper, \
    MultiprocessProcessorWrapper
from multisensor_pipeline.modules.npy import RandomArraySource, ArrayManipulationProcessor
from multisensor_pipeline.modules.console import ConsoleSink
import numpy as np
import time
from queue import Queue


class PipelineTest(TestCase):

    def setUp(self) -> None:
        pass

    def test_source_sink_wrapper(self):
        # create nodes
        source = MultiprocessSourceWrapper(module_cls=RandomArraySource, shape=(50,), frequency=50)
        sink = MultiprocessSinkWrapper(module_cls=ConsoleSink)
        queue = Queue()

        # connect nodes
        source.add_observer(sink)
        source.add_observer(queue)

        # start nodes
        sink.start()
        source.start()

        time.sleep(.1)

        sink.stop()
        source.stop()

        self.assertFalse(queue.empty())

    def test_processor_wrapper(self):

        # create nodes
        source = MultiprocessSourceWrapper(module_cls=RandomArraySource, shape=(50,), frequency=50)
        processor = MultiprocessProcessorWrapper(module_cls=ArrayManipulationProcessor, numpy_operation=np.mean)
        sink = MultiprocessSinkWrapper(module_cls=ConsoleSink)
        queue = Queue()

        # connect nodes
        source.add_observer(processor)
        processor.add_observer(sink)
        processor.add_observer(queue)

        # start nodes
        sink.start()
        processor.start()
        source.start()

        time.sleep(.1)

        sink.stop()
        processor.stop()
        source.stop()

        self.assertFalse(queue.empty())
