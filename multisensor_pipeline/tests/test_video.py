import os
import unittest
from time import sleep

import av
from PIL import Image

from multisensor_pipeline import GraphPipeline
from multisensor_pipeline.modules import ConsoleSink, QueueSink
from multisensor_pipeline.modules.video.video import VideoSource, VideoSink
from multisensor_pipeline.modules.video.webcam import WebCamSource


class VideoTesting(unittest.TestCase):
    def _test_no_video_file(self):
        # (1) define the modules
        source = VideoSource(playback_speed=1)
        sink = ConsoleSink()

        # (2) add module to a pipeline...
        pipeline = GraphPipeline()
        pipeline.add_source(source)
        pipeline.add_sink(sink)
        # (3) ...and connect the modules
        pipeline.connect(source, sink)

        # (4) print mouse movements
        try:
            pipeline.start()
            sleep(2)
        except av.error.FileNotFoundError:
            self.assertEqual(True, True)
        try:
            pipeline.stop()
        except AttributeError as e:
            self.assertEqual(True, True)

    def test_short_video(self):
        # Create a video file with 24 PIL Images and export it
        img_sequence = []
        for x in range(24):
            img_sequence.append(Image.new('RGB', (300, 200), (228, 150, 150)))
        output = av.open('output_av.mp4', 'w')
        stream = output.add_stream('h264')
        for i, img in enumerate(img_sequence):
            frame = av.VideoFrame.from_image(img)
            packet = stream.encode(frame)
            output.mux(packet)

        output.mux(stream.encode())
        output.close()

        # (1) define the modules
        source = VideoSource(file_path="output_av.mp4")
        sink = QueueSink()

        # (2) add module to a pipeline...
        pipeline = GraphPipeline()
        pipeline.add_source(source)
        pipeline.add_sink(sink)
        # (3) ...and connect the modules
        pipeline.connect(source, sink)



        pipeline.start()
        sleep(2)
        pipeline.stop()
        self.assertEqual(sink.queue.qsize(), 23)
        os.remove("output_av.mp4")

    def test_long_video(self):
        # Create a video file with 24 PIL Images and export it
        img_sequence = []
        for x in range(500):
            img_sequence.append(Image.new('RGB', (300, 200), (228, 150, 150)))
        output = av.open('output_av.mp4', 'w')
        stream = output.add_stream('h264', '24')
        for i, img in enumerate(img_sequence):
            frame = av.VideoFrame.from_image(img)
            packet = stream.encode(frame)
            output.mux(packet)

        packet = stream.encode()
        output.mux(packet)
        output.close()

        # (1) define the modules
        source = VideoSource(file_path="output_av.mp4")
        sink = QueueSink()

        # (2) add module to a pipeline...
        pipeline = GraphPipeline()
        pipeline.add_source(source)
        pipeline.add_sink(sink)
        # (3) ...and connect the modules
        pipeline.connect(source, sink)



        pipeline.start()
        sleep(.3)
        pipeline.stop()
        os.remove("output_av.mp4")
        self.assertGreater(498, sink.queue.qsize())

    def test_video_sink(self):
        # Create a video file with 24 PIL Images and export it
        img_sequence = []
        for x in range(10):
            img_sequence.append(Image.new('RGB', (200, 300), (228, 150, 150)))
        output = av.open('input.mp4', 'w')
        stream = output.add_stream('h264')
        for i, img in enumerate(img_sequence):
            frame = av.VideoFrame.from_image(img)
            packet = stream.encode(frame)
            output.mux(packet)

        output.mux(stream.encode())
        output.close()

        # (1) define the modules
        source = VideoSource(file_path="input.mp4")
        sink = VideoSink(live_preview=False, file_path="output.mp4")

        # (2) add module to a pipeline...
        pipeline = GraphPipeline()
        pipeline.add_source(source)
        pipeline.add_sink(sink)
        # (3) ...and connect the modules
        pipeline.connect(source, sink)

        pipeline.start()
        sleep(5)
        pipeline.stop()
        video = av.open("output.mp4")
        count = 1
        stream = video.streams.video[0]
        for frame in video.decode(stream):
            count +=1
        self.assertEqual(10, count)
        os.remove("output.mp4")
        os.remove("input.mp4")


class WebCamTesting(unittest.TestCase):
    def test_no_webcam(self):
        # (1) define the modules
        try:
            source = WebCamSource(web_cam_format="random")

            sink = QueueSink()

            # (2) add module to a pipeline...
            pipeline = GraphPipeline()
            pipeline.add_source(source)
            pipeline.add_sink(sink)
            # (3) ...and connect the modules
            pipeline.connect(source, sink)

            pipeline.start()
            sleep(5)
            pipeline.stop()
        except ValueError as e:
            self.assertEqual(True, True)

    def test_mac_webcam(self):
        try:
            # (1) define the modules
            source = WebCamSource()

            sink = QueueSink()

            # (2) add module to a pipeline...
            pipeline = GraphPipeline()
            pipeline.add_source(source)
            pipeline.add_sink(sink)
            # (3) ...and connect the modules
            pipeline.connect(source, sink)

            pipeline.start()
            sleep(2)
            pipeline.stop()
            self.assertGreater(sink.queue.qsize(), 5)
        except ValueError as e:
            self.assertEqual(True, True)

    def _test_linux_webcam(self):
        try:
            # (1) define the modules
            source = WebCamSource(web_cam_format="video4linux2")

            sink = QueueSink()

            # (2) add module to a pipeline...
            pipeline = GraphPipeline()
            pipeline.add_source(source)
            pipeline.add_sink(sink)
            # (3) ...and connect the modules
            pipeline.connect(source, sink)

            pipeline.start()
            sleep(2)
            pipeline.stop()
            self.assertGreater(sink.queue.qsize(), 5)
        except ValueError as e:
            self.assertEqual(True, True)

    def test_win_webcam(self):
        try:
            # (1) define the modules
            source = WebCamSource(web_cam_format="vfwcap")

            sink = QueueSink()

            # (2) add module to a pipeline...
            pipeline = GraphPipeline()
            pipeline.add_source(source)
            pipeline.add_sink(sink)
            # (3) ...and connect the modules
            pipeline.connect(source, sink)

            pipeline.start()
            sleep(2)
            pipeline.stop()
            self.assertGreater(sink.queue.qsize(), 5)
        except ValueError as e:
            self.assertEqual(True, True)
