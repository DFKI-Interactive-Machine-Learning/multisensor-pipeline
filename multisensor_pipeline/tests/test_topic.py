import unittest
from time import sleep
from typing import Optional, List
from multisensor_pipeline import BaseSource, BaseSink
from multisensor_pipeline.dataframe import MSPDataFrame, Topic
from multisensor_pipeline.pipeline.graph import GraphPipeline


class AnySource(BaseSource):
    """Source with standard topic"""

    def __init__(self):
        super(AnySource, self).__init__()
        self.list = []

    def on_update(self) -> Optional[MSPDataFrame]:
        sleep(.02)
        frame = MSPDataFrame(topic=self.output_topics[0], data=None)
        self.list.append(frame)
        return frame

    @property
    def len(self):
        return len(self.list)


class IntSource(BaseSource):
    """Source with specific topic"""

    def __init__(self):
        super(IntSource, self).__init__()
        self.list = []

    def on_update(self) -> Optional[MSPDataFrame]:
        sleep(.02)
        frame = MSPDataFrame(topic=self.output_topics[0], data=None)
        self.list.append(frame)
        return frame

    @property
    def len(self):
        return len(self.list)

    @property
    def output_topics(self) -> Optional[List[Topic]]:
        return [Topic(name='random', dtype=int)]


class AnySink(BaseSink):
    """ Sink with standard topic"""

    def __init__(self):
        super(AnySink, self).__init__()
        self.list = []

    def on_update(self, frame: MSPDataFrame):
        self.list.append(frame)

    @property
    def len(self):
        return len(self.list)


class IntSink(BaseSink):
    """ Sink with specific topic"""

    def __init__(self):
        super(IntSink, self).__init__()
        self.list = []

    def on_update(self, frame: MSPDataFrame):
        self.list.append(frame)

    @property
    def input_topics(self) -> List[Topic]:
        return [Topic(dtype=int)]

    @property
    def len(self):
        return len(self.list)


def run_pipeline(source, sink, topic=None):
    pipe = GraphPipeline()
    pipe.add([source, sink])
    pipe.connect(source, sink, topics=topic)
    pipe.start()
    sleep(0.5)
    pipe.stop()
    pipe.join()


class DownSamplingProcessorTest(unittest.TestCase):

    def test_any_any_topic(self):
        source = AnySource()
        sink = AnySink()
        run_pipeline(source, sink)
        self.assertAlmostEqual(source.len, 20, delta=2)
        self.assertAlmostEqual(sink.len, 20, delta=2)
        self.assertEqual(source.len, sink.len)

    def test_any_any_topic_filtered_with_any(self):
        source = AnySource()
        sink = AnySink()
        run_pipeline(source, sink, Topic())
        self.assertAlmostEqual(source.len, 20, delta=2)
        self.assertAlmostEqual(sink.len, 20, delta=2)
        self.assertEqual(source.len, sink.len)

    def test_any_any_topic_filtered_with_specific(self):
        source = AnySource()
        sink = AnySink()
        run_pipeline(source, sink, Topic(dtype=int))
        self.assertAlmostEqual(source.len, 20, delta=2)
        self.assertEqual(sink.len, 0)

    def test_any_specific_topic(self):
        source = AnySource()
        sink = IntSink()
        try:
            run_pipeline(source, sink)
        except AssertionError:
            self.assertTrue(True)

    def test_any_specific_topic_filtered_with_any(self):
        source = AnySource()
        sink = IntSink()
        try:
            run_pipeline(source, sink, Topic())
        except AssertionError:
            self.assertTrue(True)

    def test_any_specific_topic_filtered_with_specific(self):
        source = AnySource()
        sink = IntSink()
        try:
            run_pipeline(source, sink, Topic(dtype=int))
        except AssertionError:
            self.assertTrue(True)

    def test_specific_any_topic(self):
        source = IntSource()
        sink = AnySink()
        run_pipeline(source, sink)
        self.assertAlmostEqual(source.len, 20, delta=2)
        self.assertAlmostEqual(sink.len, 20, delta=2)
        self.assertEqual(source.len, sink.len)

    def test_specific_any_topic_filtered_with_any(self):
        # TODO: What should happen here?
        source = IntSource()
        sink = AnySink()
        run_pipeline(source, sink, Topic())

    def test_specific_any_topic_filtered_with_specific(self):
        # TODO: What should happen here?
        source = IntSource()
        sink = AnySink()
        run_pipeline(source, sink, Topic(dtype=int))

    def test_specific_specific_topic(self):
        source = IntSource()
        sink = IntSink()
        run_pipeline(source, sink)
        self.assertAlmostEqual(source.len, 20, delta=2)
        self.assertAlmostEqual(sink.len, 20, delta=2)
        self.assertEqual(source.len, sink.len)

    def test_specific_specific_topic_filtered_with_any(self):
        # TODO: What should happen here?
        source = IntSource()
        sink = IntSink()
        run_pipeline(source, sink, Topic())


    def test_specific_specific_topic_filtered_with_specific(self):
        source = IntSource()
        sink = IntSink()
        run_pipeline(source, sink, Topic(name="random", dtype=int))
        self.assertAlmostEqual(source.len, 20, delta=2)
        self.assertAlmostEqual(sink.len, 20, delta=2)
        self.assertEqual(source.len, sink.len)
