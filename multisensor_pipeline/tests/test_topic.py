import unittest
from time import sleep
from typing import Optional, List
from multisensor_pipeline import BaseSource, BaseSink
from multisensor_pipeline.modules.base.sampler import BaseFixedRateSource
from multisensor_pipeline.dataframe import MSPDataFrame, Topic
from multisensor_pipeline.pipeline.graph import GraphPipeline


SLEEPTIME = 1.
FREQUENCY = 10.
PERIOD_TIME = 1. / FREQUENCY
NUM_SAMPLES = FREQUENCY * SLEEPTIME


class AnySource(BaseFixedRateSource):
    """Source with standard topic"""

    def __init__(self):
        super(AnySource, self).__init__(samplerate=FREQUENCY)
        self.list = []

    def on_update(self) -> Optional[MSPDataFrame]:
        frame = MSPDataFrame(topic=Topic(name='random', dtype=int), data=1)
        self.list.append(frame)
        return frame

    @property
    def len(self):
        return len(self.list)


class IntSource(BaseFixedRateSource):
    """Source with specific topic"""

    def __init__(self):
        super(IntSource, self).__init__(samplerate=FREQUENCY)
        self.list = []

    def on_update(self) -> Optional[MSPDataFrame]:
        frame = MSPDataFrame(topic=self.output_topics[0], data=0)
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
    sleep(SLEEPTIME)
    pipe.stop()
    pipe.join()


class TopicTest(unittest.TestCase):

    def test_topic_equals(self):
        t_int = Topic(dtype=int)
        t_bool = Topic(dtype=bool)
        t_int_n = Topic(name="int", dtype=int)
        t_int_n_rand = Topic(name="random", dtype=int)
        t_bool_n = Topic(name="bool", dtype=bool)

        # self equal checks should always be true
        self.assertEqual(Topic(), Topic())
        self.assertEqual(t_int, t_int)
        self.assertEqual(t_int_n, t_int_n)

        # Any topic matches with the Any-Topic => Topic() (in both directions)
        # Sink accepts Any-Topic (Example: ConsoleSink)
        self.assertEqual(t_int_n, Topic())
        self.assertEqual(t_int, Topic())
        # Source offers Any-Topic (Example: ReplaySource / backwards compatability)
        self.assertEqual(Topic(), t_int)
        self.assertEqual(Topic(), t_int_n)

        # dtype must match
        self.assertNotEqual(t_int, t_bool)
        self.assertNotEqual(t_int, t_bool_n)

        # specific topic of source can be consumed by less specific sink, but not the other way round
        self.assertEqual(t_int_n, t_int)
        self.assertNotEqual(t_int, t_int_n)

        # name makes a difference, if defined for both
        self.assertNotEqual(t_int_n, t_int_n_rand)

        # you cannot define a name only, a name always refines a given dtype
        with self.assertRaises(AssertionError):
            Topic(name="int")
        pass

    def test_any_any_topic(self):
        source = AnySource()
        sink = AnySink()
        run_pipeline(source, sink)
        self.assertAlmostEqual(NUM_SAMPLES, source.len, delta=0)
        self.assertAlmostEqual(NUM_SAMPLES, sink.len, delta=0)
        self.assertEqual(source.len, sink.len)

    def test_any_any_topic_filtered_with_any(self):
        source = AnySource()
        sink = AnySink()
        run_pipeline(source, sink, Topic())
        self.assertAlmostEqual(NUM_SAMPLES, source.len, delta=0)
        self.assertAlmostEqual(NUM_SAMPLES, sink.len, delta=0)
        self.assertEqual(source.len, sink.len)

    def test_any_any_topic_filtered_with_specific(self):
        source = AnySource()
        sink = AnySink()
        run_pipeline(source, sink, Topic(dtype=bool))
        self.assertAlmostEqual(NUM_SAMPLES, source.len, delta=0)
        self.assertEqual(0, sink.len)

    def test_any_specific_topic(self):
        source = AnySource()
        sink = IntSink()
        run_pipeline(source, sink)
        self.assertAlmostEqual(NUM_SAMPLES, source.len, delta=0)
        self.assertAlmostEqual(NUM_SAMPLES, sink.len, delta=0)
        self.assertEqual(source.len, sink.len)

    def test_any_specific_topic_filtered_with_specific_correct(self):
        source = AnySource()
        sink = IntSink()
        run_pipeline(source, sink, Topic(dtype=int))

    def test_any_specific_topic_filtered_with_specific_wrong(self):
        source = AnySource()
        sink = IntSink()
        with self.assertRaises(AssertionError):
            run_pipeline(source, sink, Topic(dtype=bool))

    def test_specific_any_topic(self):
        source = IntSource()
        sink = AnySink()
        run_pipeline(source, sink)
        self.assertAlmostEqual(NUM_SAMPLES, source.len, delta=0)
        self.assertAlmostEqual(NUM_SAMPLES, sink.len, delta=0)
        self.assertEqual(source.len, sink.len)

    def test_specific_any_topic_filtered_with_specific_correct(self):
        source = IntSource()
        sink = AnySink()
        run_pipeline(source, sink, Topic(dtype=int))

    def test_specific_any_topic_filtered_with_specific_wrong(self):
        source = IntSource()
        sink = AnySink()
        with self.assertRaises(AssertionError):
            run_pipeline(source, sink, Topic(dtype=bool))

    def test_specific_specific_topic(self):
        source = IntSource()
        sink = IntSink()
        run_pipeline(source, sink)
        self.assertAlmostEqual(NUM_SAMPLES, source.len, delta=0)
        self.assertAlmostEqual(NUM_SAMPLES, sink.len, delta=0)
        self.assertEqual(source.len, sink.len)

    def test_specific_specific_topic_filtered_with_specific_wrong(self):
        source = IntSource()
        sink = IntSink()
        with self.assertRaises(AssertionError):
            run_pipeline(source, sink, Topic(dtype=bool))

    def test_specific_specific_topic_filtered_with_specific_correct(self):
        source = IntSource()
        sink = IntSink()
        run_pipeline(source, sink, Topic(dtype=int))
        self.assertAlmostEqual(NUM_SAMPLES, source.len, delta=0)
        self.assertAlmostEqual(NUM_SAMPLES, sink.len, delta=0)
        self.assertEqual(source.len, sink.len)

    def test_specific_specific_topic_filtered_with_specific_name_correct(self):
        source = IntSource()
        sink = IntSink()
        run_pipeline(source, sink, Topic(name="random"))
        self.assertAlmostEqual(NUM_SAMPLES, source.len, delta=0)
        self.assertAlmostEqual(NUM_SAMPLES, sink.len, delta=0)
        self.assertEqual(source.len, sink.len)
