import unittest
from time import sleep
from datetime import datetime
import logging
from typing import Optional, List
from random import randint
import numpy as np
from multisensor_pipeline.dataframe.dataframe import MSPDataFrame, Topic
from multisensor_pipeline.modules.base.base import BaseSource, BaseProcessor
from multisensor_pipeline.modules.npy import RandomArraySource, ArrayManipulationProcessor
from multisensor_pipeline.modules import QueueSink, ConsoleSink, SleepTrashSink, SleepPassthroughProcessor, ListSink, \
    PassthroughProcessor, TrashSink
from multisensor_pipeline.pipeline.graph import GraphPipeline

logging.basicConfig(level=logging.DEBUG)


class RandomIntSource(BaseSource):
    """Generate 50 random integer numbers per second."""

    def on_update(self) -> Optional[MSPDataFrame]:
        sleep(.02)
        return MSPDataFrame(topic=self.output_topics[0], data=randint(0, 100))

    @property
    def output_topics(self) -> Optional[List[Topic]]:
        return [Topic(name='random', dtype=int)]


class ConstraintCheckingProcessor(BaseProcessor):
    """Checks, if incoming integer values are greater than 50."""

    def on_update(self, frame: MSPDataFrame) -> Optional[MSPDataFrame]:
        return MSPDataFrame(topic=self.input_topics[0], data=frame.data > 50)

    @property
    def input_topics(self) -> List[Topic]:
        return [Topic(dtype=int)]

    @property
    def output_topics(self) -> Optional[List[Topic]]:
        return [Topic(name='constraint_check', dtype=bool)]


class BaseTestCase(unittest.TestCase):
    def test_pipeline_example(self):
        pipeline = GraphPipeline()
        source_vector = RandomArraySource(shape=(50,), sampling_rate=50)
        source_scalar = RandomArraySource(sampling_rate=50)
        processor_mean = ArrayManipulationProcessor(np.mean)
        processor_std = ArrayManipulationProcessor(np.std)
        sink = QueueSink()

        assert len(pipeline.source_nodes) == 0

        pipeline.add_source(source_vector)

        assert len(pipeline.source_nodes) == 1
        assert len(pipeline.processor_nodes) == 0
        assert len(pipeline.sink_nodes) == 0

        pipeline.add_source(source_scalar)
        assert len(pipeline.source_nodes) == 2
        assert len(pipeline.processor_nodes) == 0
        assert len(pipeline.sink_nodes) == 0

        pipeline.add_processor(processor_mean)
        assert len(pipeline.source_nodes) == 2
        assert len(pipeline.processor_nodes) == 1
        assert len(pipeline.sink_nodes) == 0

        pipeline.add_processor(processor_std)
        assert len(pipeline.source_nodes) == 2
        assert len(pipeline.processor_nodes) == 2
        assert len(pipeline.sink_nodes) == 0

        pipeline.add_sink(sink)
        assert len(pipeline.source_nodes) == 2
        assert len(pipeline.processor_nodes) == 2
        assert len(pipeline.sink_nodes) == 1

        with self.assertRaises(AssertionError):
            pipeline.check_pipeline()

        pipeline.connect(source_vector, processor_mean)
        pipeline.connect(source_vector, processor_std)
        pipeline.connect(source_scalar, sink)
        pipeline.connect(processor_mean, sink)
        pipeline.connect(processor_std, sink)
        assert pipeline.size == 5

        pipeline.start()
        assert len(pipeline.active_modules) == 5

        sleep(1)

        pipeline.stop()
        pipeline.join()
        assert len(pipeline.active_modules) == 0

        assert not sink.empty()

    def test_minimal_example_I(self):
        # define the modules
        source = RandomArraySource(shape=None, sampling_rate=60)
        sink = ConsoleSink()

        # add module to a pipeline...
        pipeline = GraphPipeline()
        pipeline.add(modules=[source, sink])
        # ...and connect the modules
        pipeline.connect(module=source, successor=sink, topics=source.output_topics[0])

        # print mean of random numbers for 0.1 seconds
        pipeline.start()
        sleep(.1)
        pipeline.stop()
        pipeline.join()

    def test_minimal_example_II(self):
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
        assert True

    def test_passthrough_processor(self):
        # define the modules
        source = RandomArraySource(sampling_rate=100, max_count=10)
        processor = PassthroughProcessor()
        sink = ListSink()

        # add module to a pipeline...
        pipeline = GraphPipeline()
        pipeline.add(modules=[source, processor, sink])
        # ...and connect the modules
        pipeline.connect(module=source, successor=processor)
        pipeline.connect(module=processor, successor=sink)

        # print result of the constraint checker for 0.1 seconds
        pipeline.start()
        sleep(.5)
        pipeline.stop()
        pipeline.join()
        self.assertEqual(len(sink), 10)

    def test_sleep_passthrough_processor(self):
        # define the modules
        source = RandomArraySource(sampling_rate=10, max_count=10)
        processor = SleepPassthroughProcessor(.5)
        sink = ListSink()

        # add module to a pipeline...
        pipeline = GraphPipeline()
        pipeline.add(modules=[source, processor, sink])
        # ...and connect the modules
        pipeline.connect(module=source, successor=processor)
        pipeline.connect(module=processor, successor=sink)

        # print result of the constraint checker for 0.1 seconds
        start_time = datetime.now()
        pipeline.start()
        sleep(1)
        pipeline.stop()
        pipeline.join()
        end_time = datetime.now()
        self.assertEqual((end_time - start_time).seconds, 5)
        self.assertEqual(len(sink), 10)

    def test_trash_sink(self):
        # define the modules
        source = RandomArraySource(sampling_rate=100, max_count=10)
        list_sink = ListSink()
        trash_sink = TrashSink()

        # add module to a pipeline...
        pipeline = GraphPipeline()
        pipeline.add(modules=[source, list_sink, trash_sink])
        # ...and connect the modules
        pipeline.connect(module=source, successor=list_sink)
        pipeline.connect(module=source, successor=trash_sink)

        # print result of the constraint checker for 0.1 seconds
        pipeline.start()
        sleep(.5)
        pipeline.stop()
        pipeline.join()
        self.assertEqual(len(list_sink), 10)
        self.assertEqual(trash_sink.counter, 10)

    def test_sleep_trash_sink(self):
        # define the modules
        source = RandomArraySource(sampling_rate=100, max_count=10)
        list_sink = ListSink()
        sleep_trash_sink = SleepTrashSink(.5)

        # add module to a pipeline...
        pipeline = GraphPipeline()
        pipeline.add(modules=[source, list_sink, sleep_trash_sink])
        # ...and connect the modules
        pipeline.connect(module=source, successor=list_sink)
        pipeline.connect(module=source, successor=sleep_trash_sink)

        # print result of the constraint checker for 0.1 seconds
        start_time = datetime.now()
        pipeline.start()
        sleep(1)
        pipeline.stop()
        pipeline.join()
        end_time = datetime.now()
        self.assertEqual(len(list_sink), 10)
        self.assertEqual(sleep_trash_sink.counter, 10)
        self.assertEqual((end_time - start_time).seconds, 5)

