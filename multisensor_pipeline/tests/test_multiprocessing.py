import time
import logging
import unittest

import numpy as np

from multisensor_pipeline.modules.multiprocess import MultiprocessSourceWrapper, MultiprocessSinkWrapper, \
    MultiprocessProcessorWrapper
from multisensor_pipeline.modules.npy import RandomArraySource, ArrayManipulationProcessor
from multisensor_pipeline.modules import PassthroughProcessor, QueueSink, ConsoleSink, ListSink
from multisensor_pipeline.pipeline.graph import GraphPipeline
from multisensor_pipeline.dataframe import MSPDataFrame, Topic
import multiprocessing as mp

logging.basicConfig(level=logging.DEBUG)


class MultiprocessingTestCase(unittest.TestCase):

    @staticmethod
    def _worker(queue_in: mp.Queue, queue_out: mp.Queue):
        df = queue_in.get()
        queue_out.put(df)

    def test_dataframe_interprocess_transfer(self):
        df_in = MSPDataFrame(data={"a": 1, "b": 2}, topic=Topic(name="test", dtype=dict))

        queue_in = mp.Queue()
        queue_out = mp.Queue()
        process = mp.Process(target=MultiprocessingTestCase._worker, args=(queue_in, queue_out))
        process.start()

        queue_in.put(df_in)
        df_out = queue_out.get()

        process.join()
        self.assertEqual(df_in.data, df_out.data)

    def test_source_wrapper(self):
        # create nodes
        source = MultiprocessSourceWrapper(
            module_cls=RandomArraySource,
            shape=(5,),
            sampling_rate=50,
        )
        sink = ListSink()

        # connect nodes
        source.add_observer(sink)

        # start nodes
        sink.start()
        source.start()

        time.sleep(.5)

        # sink.stop(blocking=False)
        source.stop(blocking=False)
        sink.join()

        time.sleep(2)

        self.assertFalse(source._process.is_alive())
        self.assertFalse(source._thread.is_alive())
        self.assertFalse(sink._thread.is_alive())

    def test_source_sink_wrapper(self):
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

        time.sleep(2)

        self.assertFalse(source._process.is_alive())
        self.assertFalse(source._thread.is_alive())
        self.assertFalse(sink._process.is_alive())
        self.assertFalse(sink._thread.is_alive())

        queue.join()

        self.assertFalse(queue.empty())

    def test_processor_wrapper(self):
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

        self.assertFalse(queue.empty())

    def test_parallelized_pipeline(self):
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
        sink = ListSink()

        # add modules to a pipeline
        pipeline = GraphPipeline()
        pipeline.add_source(source)
        pipeline.add_processor(processor1)
        pipeline.add_processor(processor2)
        pipeline.add_sink(sink)

        # connect modules
        pipeline.connect(source, processor1)
        pipeline.connect(processor1, processor2)
        pipeline.connect(processor2, sink)

        pipeline.start()
        time.sleep(1.25)
        pipeline.stop()

        self.assertGreater(len(sink), 0)
