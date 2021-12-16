import unittest
from time import sleep
from PIL.Image import Image
from multisensor_pipeline import GraphPipeline
from multisensor_pipeline.dataframe import Topic
from multisensor_pipeline.modules import ListSink
from multisensor_pipeline.modules.video import WebcamSource


class WebcamTests(unittest.TestCase):
    def test_simple_webcam(self):
        self.simple_webcam()

    def test_simple_webcam_filter(self):
        topic = Topic(name="frame", dtype=Image)
        self.simple_webcam(topic=topic)

    def simple_webcam(self, topic=None):
        # (1) define the modules
        framerate = 15
        webcam_id = WebcamSource.available_webcams()[0]
        source = WebcamSource(webcam_id=webcam_id, framerate=framerate)
        sink = ListSink()

        # (2) add module to a pipeline...
        pipeline = GraphPipeline()
        pipeline.add_source(source)
        pipeline.add_sink(sink)

        # (3) ...and connect the modules
        pipeline.connect(source, sink, topics=topic)

        # Test
        pipeline.start()
        sleep(2)
        pipeline.stop()
        pipeline.join()

        # for i, img_frame in enumerate(sink.list):
        #     img_frame.data.save(f"test{i}.jpg")

        self.assertTrue(2*framerate - 1 <= len(sink) <= 2*framerate + 3)
