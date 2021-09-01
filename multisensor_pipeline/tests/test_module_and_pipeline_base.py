import unittest
from time import sleep
import logging
from typing import Optional
from random import randint
import math

import numpy as np
import pytest

from multisensor_pipeline.dataframe.dataframe import MSPDataFrame
from multisensor_pipeline.modules.base.base import BaseSource, BaseProcessor
from multisensor_pipeline.modules.npy import RandomArraySource, ArrayManipulationProcessor
from multisensor_pipeline.modules import QueueSink, ConsoleSink, SleepTrashSink, SleepPassthroughProcessor, ListSink
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

        with pytest.raises(AssertionError):
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
        pipeline.connect(module=source, successor=sink, topics=source.OutputTopics.random_int.value)

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

    def test_dropout_example(self):
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

        assert abs(num_received - num_expected) <= 2
