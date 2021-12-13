import os
import unittest
from time import sleep
from typing import List
import av
from PIL import Image
from multisensor_pipeline.modules import ConsoleSink, ListSink
from multisensor_pipeline.modules.video.video import VideoSource, VideoSink
from multisensor_pipeline.pipeline.graph import GraphPipeline


class VideoTesting(unittest.TestCase):

    @staticmethod
    def _create_test_video(filename, num_frames=1):
        img_sequence: List[Image] = [Image.new('RGB', (300, 200), (228, 150, 150)) for _ in range(num_frames)]
        output = av.open(filename, 'w')
        stream = output.add_stream('h264', '24')
        for img in img_sequence:
            frame = av.VideoFrame.from_image(img)
            packet = stream.encode(frame)
            output.mux(packet)
        output.mux(stream.encode())
        output.close()

    def test_no_video_file(self):
        # (1) define the modules
        source = VideoSource(file="invalid.mp4", playback_speed=1)
        sink = ConsoleSink()

        # (2) add module to a pipeline...
        pipeline = GraphPipeline()
        pipeline.add_source(source)
        pipeline.add_sink(sink)

        # (3) ...and connect the modules
        pipeline.connect(source, sink)

        # (4) print mouse movements
        with self.assertRaises(av.error.FileNotFoundError):
            pipeline.start()
            sleep(2)

        with self.assertRaises(AttributeError):
            pipeline.stop()

    def _test_video_source(self, num_frames, playback_speed=float("inf")):
        self._create_test_video(filename="output_av.mp4", num_frames=num_frames)

        # (1) define the modules
        source = VideoSource(file="output_av.mp4", playback_speed=playback_speed)
        sink = ListSink()

        # (2) add module to a pipeline...
        pipeline = GraphPipeline()
        pipeline.add_source(source)
        pipeline.add_sink(sink)

        # (3) ...and connect the modules
        pipeline.connect(source, sink)

        # Test
        pipeline.start()
        sleep(1.)
        pipeline.stop()
        pipeline.join()

        # Assert
        self.assertAlmostEqual(len(sink), num_frames, delta=2)

        # Cleanup
        os.remove("output_av.mp4")

    def test_short_video(self):
        self._test_video_source(num_frames=24, playback_speed=1.)

    def test_long_video(self):
        self._test_video_source(num_frames=250)

    def _test_video_sink(self, topic_filtering=False):
        num_frames = 10
        self._create_test_video("input.mp4", num_frames=num_frames)

        # (1) define the modules
        source = VideoSource(file="input.mp4")
        sink = VideoSink(file_path="output.mp4")

        # (2) add module to a pipeline...
        pipeline = GraphPipeline()
        pipeline.add_source(source)
        pipeline.add_sink(sink)

        # (3) ...and connect the modules
        topics = None if topic_filtering is False else source.output_topics[0]
        pipeline.connect(source, sink, topics=topics)

        # Test
        pipeline.start()
        sleep(1.)
        pipeline.stop()
        pipeline.join()

        # Assert
        video = av.open("output.mp4")
        stream = video.streams.video[0]
        count = 1 + sum(1 for _ in video.decode(stream))
        video.close()
        self.assertEqual(num_frames, count)

        # Cleanup
        os.remove("output.mp4")
        os.remove("input.mp4")

    def test_video_sink_simple(self):
        self._test_video_sink(topic_filtering=False)

    def test_video_sink_simple_topic_filter(self):
        self._test_video_sink(topic_filtering=True)
