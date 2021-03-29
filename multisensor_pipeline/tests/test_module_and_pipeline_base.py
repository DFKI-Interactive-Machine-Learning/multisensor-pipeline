from unittest import TestCase
from multisensor_pipeline.pipeline import GraphPipeline
import numpy as np
from time import sleep
from multisensor_pipeline.modules.npy import RandomArraySource, ArrayManipulationProcessor
from multisensor_pipeline.modules import QueueSink, ConsoleSink
import logging


logging.basicConfig(level=logging.DEBUG)


class MultiprocessingPipelineTest(TestCase):

    def setUp(self) -> None:
        self.pipeline = GraphPipeline()
        self.src1 = RandomArraySource(shape=(50,), sampling_rate=50)
        self.src2 = RandomArraySource(sampling_rate=50)
        self.p1 = ArrayManipulationProcessor(np.mean)
        self.p2 = ArrayManipulationProcessor(np.std)
        self.sink = QueueSink()

    def test_pipeline(self):
        self.assertEqual(len(self.pipeline.source_nodes), 0)

        self.pipeline.add_source(self.src1)

        self.assertEqual(len(self.pipeline.source_nodes), 1)
        self.assertEqual(len(self.pipeline.processor_nodes), 0)
        self.assertEqual(len(self.pipeline.sink_nodes), 0)

        self.pipeline.add_source(self.src2)
        self.assertEqual(len(self.pipeline.source_nodes), 2)
        self.assertEqual(len(self.pipeline.processor_nodes), 0)
        self.assertEqual(len(self.pipeline.sink_nodes), 0)

        self.pipeline.add_processor(self.p1)
        self.assertEqual(len(self.pipeline.source_nodes), 2)
        self.assertEqual(len(self.pipeline.processor_nodes), 1)
        self.assertEqual(len(self.pipeline.sink_nodes), 0)

        self.pipeline.add_processor(self.p2)
        self.assertEqual(len(self.pipeline.source_nodes), 2)
        self.assertEqual(len(self.pipeline.processor_nodes), 2)
        self.assertEqual(len(self.pipeline.sink_nodes), 0)

        self.pipeline.add_sink(self.sink)
        self.assertEqual(len(self.pipeline.source_nodes), 2)
        self.assertEqual(len(self.pipeline.processor_nodes), 2)
        self.assertEqual(len(self.pipeline.sink_nodes), 1)

        with self.assertRaises(AssertionError):
            self.pipeline.check_pipeline()

        self.pipeline.connect(self.src1, self.p1)
        self.pipeline.connect(self.src1, self.p2)
        self.pipeline.connect(self.src2, self.sink)
        self.pipeline.connect(self.p1, self.sink)
        self.pipeline.connect(self.p2, self.sink)
        self.assertEqual(self.pipeline.size, 5)

        self.pipeline.start()
        self.assertEqual(len(self.pipeline.active_modules), 5)

        sleep(1)

        self.pipeline.stop()
        self.pipeline.join()
        self.assertEqual(len(self.pipeline.active_modules), 0)

        self.assertFalse(self.sink.empty())

    def test_minimal_example(self):
        return True
        # define the modules
        source = RandomArraySource(shape=(50,), sampling_rate=60)
        processor = ArrayManipulationProcessor(np.mean)
        sink = ConsoleSink()

        # add module to a pipeline...
        pipeline = GraphPipeline()
        pipeline.add_source(source)
        pipeline.add_processor(processor)
        pipeline.add_sink(sink)
        # ...and connect the modules
        pipeline.connect(source, processor)
        pipeline.connect(processor, sink)
        # (optional) add another edge to print all random numbers
        pipeline.connect(source, sink)

        # print mean of random numbers for 0.1 seconds
        pipeline.start()
        sleep(.1)
        pipeline.stop()
