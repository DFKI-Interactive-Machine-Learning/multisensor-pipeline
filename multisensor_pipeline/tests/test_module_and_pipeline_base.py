from unittest import TestCase
import numpy as np
from time import sleep

from multisensor_pipeline.dataframe.dataframe import MSPDataFrame
from multisensor_pipeline.modules.base.base import BaseSource, BaseProcessor
from multisensor_pipeline.modules.npy import RandomArraySource, \
    ArrayManipulationProcessor
from multisensor_pipeline.modules import QueueSink, ConsoleSink, \
    SleepTrashSink, SleepPassthroughProcessor, ListSink
import logging
from typing import Optional
from random import randint
import math

from multisensor_pipeline.pipeline.graph import GraphPipeline

logging.basicConfig(level=logging.DEBUG)


class RandomIntSource(BaseSource):
    """Generate 50 random numbers per second."""

    def on_update(self) -> Optional[MSPDataFrame]:
        sleep(.02)
        topic = self._generate_topic(name='random', dtype=int)
        return MSPDataFrame(topic=topic, value=randint(0, 100))


class ConstraintCheckingProcessor(BaseProcessor):
    """Checks, if incoming values are greater than 50."""

    def on_update(self, frame: MSPDataFrame) -> Optional[MSPDataFrame]:
        topic = self._generate_topic(name='constraint_check', dtype=bool)
        return MSPDataFrame(topic=topic, value=frame["value"] > 50)


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
        # define the modules
        source = RandomArraySource(shape=(50,), sampling_rate=60)
        processor = ArrayManipulationProcessor(numpy_operation=np.mean)
        sink = ConsoleSink()

        # add module to a pipeline...
        pipeline = GraphPipeline()
        pipeline.add(modules=[source, processor, sink])
        # ...and connect the modules
        pipeline.connect(module=source, successor=processor)
        pipeline.connect(module=processor, successor=sink)
        # (optional) add another edge to print all random numbers
        pipeline.connect(module=source, successor=sink)

        # print mean of random numbers for 0.1 seconds
        pipeline.start()
        sleep(.1)
        pipeline.stop()
        pipeline.join()

    def test_custom_modules_example(self):
        # define the modules
        source = RandomIntSource()
        processor = ConstraintCheckingProcessor()
        sink = ConsoleSink()

        # add module to a pipeline...
        pipeline = GraphPipeline()
        pipeline.add(modules=[source, processor, sink])
        # ...and connect the modules
        pipeline.connect(module=source, successor=processor)
        pipeline.connect(module=processor, successor=sink)

        # print result of the constraint checker for 0.1 seconds
        pipeline.start()
        sleep(.1)
        pipeline.stop()
        pipeline.join()

    def test_dropout(self):
        dropout_threshold = .2
        sleep_time = .5

        # source - sink pipeline
        source = RandomArraySource(sampling_rate=10)
        sink = SleepTrashSink(
            sleep_time=dropout_threshold,
            dropout=dropout_threshold,
        )

        p = GraphPipeline()
        p.add([source, sink])
        p.connect(source, sink)
        p.start()

        sleep(sleep_time)

        p.stop()
        p.join()

        # source - processor - sink pipeline
        source = RandomArraySource(sampling_rate=10)
        processor = SleepPassthroughProcessor(
            sleep_time=dropout_threshold,
            dropout=dropout_threshold,
        )
        sink = ListSink()

        p = GraphPipeline()
        p.add([source, processor, sink])
        p.connect(source, processor)
        p.connect(processor, sink)

        p.start()
        sleep(sleep_time)
        p.stop()
        p.join()

        num_received = len(sink.list)
        num_expected = math.ceil(1. / dropout_threshold * sleep_time)

        self.assertTrue(abs(num_received - num_expected) <= 2)
