from unittest import TestCase
from multisensor_pipeline.pipeline import GraphPipeline
import numpy as np
from queue import Queue
from time import sleep
from multisensor_pipeline.modules.numpy import RandomArraySource, ArrayManipulationProcessor
from multisensor_pipeline.modules.console import ConsoleSink

class PipelineTest(TestCase):

    def setUp(self) -> None:
        self.pipeline = GraphPipeline()
        self.src1 = RandomArraySource(shape=(50,), frequency=50)
        self.src2 = RandomArraySource(frequency=50)
        self.p1 = ArrayManipulationProcessor(np.mean)
        self.p2 = ArrayManipulationProcessor(np.std)
        self.sink = Queue()

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
        active_nodes = self.pipeline.get_nodes_with_attribute("active", True)
        self.assertEqual(len(active_nodes), 5)

        sleep(.1)

        self.pipeline.stop()
        inactive_nodes = self.pipeline.get_nodes_with_attribute("active", False)
        self.assertEqual(len(inactive_nodes), 5)

        self.assertFalse(self.sink.empty())

    def test_minimal_example(self):
        # define the modules
        source = RandomArraySource(shape=(50,), frequency=60)
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
