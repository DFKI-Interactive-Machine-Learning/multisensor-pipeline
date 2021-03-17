from unittest import TestCase
from multisensor_pipeline.utils.dataframe import TypeInfo, TypeMismatchException
from copy import deepcopy
from queue import Queue
from multisensor_pipeline.modules.numpy import RandomArraySource, ArrayManipulationProcessor
from multisensor_pipeline.modules.base import BaseSink
from multisensor_pipeline.pipeline import GraphPipeline
import numpy as np


class TestTypeInfo(TestCase):

    def test_type_info(self):
        attributes = {"attr1": 1, "attr2": 2}
        info1 = TypeInfo(name="name", dtype=int, **attributes)
        self.assertEqual(info1, deepcopy(info1))

        info2 = deepcopy(info1)
        info2._source = "unittest"
        info2._name = "othername"
        self.assertEqual(info1, info2)

        info2._dtype = float
        self.assertNotEqual(info1, info2)

        offers = [info1, info1]
        consumes = [info2, info2]
        self.assertFalse(info1.matches(consumes))
        # self.assertFalse(TypeInfo.multi_match(offers, consumes))
        self.assertTrue(info1.matches(consumes + [info1]))
        # self.assertTrue(TypeInfo.multi_match(offers + [info2], consumes))

    def test_multi_match(self):
        valid_source = RandomArraySource()
        valid_processor = ArrayManipulationProcessor(np.mean)
        valid_sink = Queue()

        class InvalidSink(BaseSink):

            def __init__(self):
                super().__init__()
                self._consumes = [TypeInfo(dtype=str, name="invalid_sink")]

            def _update(self, frame=None):
                pass

        invalid_sink = InvalidSink()

        # int to generic works
        self.assertTrue(TypeInfo.multi_match(valid_source, valid_processor))
        self.assertTrue(TypeInfo.multi_match(valid_source, valid_sink))

        # str and int should not work
        self.assertFalse(TypeInfo.multi_match(valid_source, invalid_sink))

        # generic to str should pass; it's the responsibility of the developer in this case
        self.assertTrue(TypeInfo.multi_match(valid_processor, invalid_sink))

        # test with pipeline
        p = GraphPipeline()
        p.add_source(valid_source)
        p.add_processor(valid_processor)
        p.add_sink(valid_sink)
        p.connect(valid_source, valid_sink)
        p.connect(valid_source, valid_processor)
        p.connect(valid_processor, valid_sink)
        self.assertTrue(p.check_pipeline())

        p.add_sink(invalid_sink)
        p.connect(valid_processor, invalid_sink)  # won't work during runtime, but shall not raise an exception
        self.assertTrue(p.check_pipeline())
        size_before_error = p.size

        with self.assertRaises(TypeMismatchException):
            p.connect(valid_source, invalid_sink)

        self.assertTrue(p.check_pipeline())  # shall pass, because nothing was added
        self.assertEqual(size_before_error, p.size)










