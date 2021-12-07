import sys
import unittest
from time import sleep
import av
from PIL.Image import Image
from multisensor_pipeline import GraphPipeline
from multisensor_pipeline.dataframe import Topic
from multisensor_pipeline.modules import QueueSink, ListSink
from multisensor_pipeline.modules.video import WebCamSource


def is_running_on_linux() -> bool:
    """Return whether this is running on Linux (Ubuntu, etc.)."""
    return sys.platform.startswith('linux')


def is_running_on_macos() -> bool:
    """Return whether this is running on macOS (Darwin)."""
    return sys.platform.startswith('darwin')


def is_running_on_windows() -> bool:
    """Return weather this is running under Windows."""
    return sys.platform.startswith('win32')


class WebCamTests(unittest.TestCase):
    def test_simple_webcam(self):
        if is_running_on_windows():
            self.simple_webcam_windows()
        elif is_running_on_linux():
            self.simple_webcam_linux()
        elif is_running_on_macos():
            self.simple_webcam_macos()

    def test_simple_webcam_filter(self):
        topic = Topic(name="frame", dtype=Image)
        if is_running_on_windows():
            self.simple_webcam_windows(topic=topic)
        elif is_running_on_linux():
            self.simple_webcam_linux(topic=topic)
        elif is_running_on_macos():
            self.simple_webcam_macos(topic=topic)

    def simple_webcam_windows(self, topic=None):
        # (1) define the modules
        source = WebCamSource(web_cam_format="dshow", web_cam_id="video=HD WebCam", options={'framerate': '10'})
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

        # Assert
        self.assertAlmostEqual(len(sink), 20, delta=1)

    def simple_webcam_linux(self, topic=None):
        # (1) define the modules
        webcam_source = None
        webcam_identifiers = (
            '/dev/video0',
            '/dev/video1',
            '/dev/video2',
        )
        for webcam_identifier in webcam_identifiers:
            try:
                print(f'Trying webcam at {webcam_identifier} ...')
                webcam_source = WebCamSource(
                    web_cam_format="video4linux2",
                    web_cam_id=webcam_identifier,
                    options={
                        'framerate': '5',
                    }
                )
            except (av.error.FileNotFoundError, av.error.OSError):
                pass
        if webcam_source is None:
            print(
                f'Could not find a webcam under Linux. '
                f'Tried: {webcam_identifiers} '
                f'Thus, skipping this tests_ci. '
                f'Test coverage may be reduced.'
            )
            return

        sink = QueueSink()

        # (2) add module to a pipeline...
        pipeline = GraphPipeline()
        pipeline.add_source(webcam_source)
        pipeline.add_sink(sink)

        # (3) ...and connect the modules
        pipeline.connect(webcam_source, sink, topics=topic)

        # Test
        pipeline.start()
        sleep(2)
        pipeline.stop()
        pipeline.join()

        # Assert
        assert sink.queue.qsize() >= 10

    def simple_webcam_macos(self, topic=None):
        # (1) define the modules
        source = WebCamSource(options={"framerate": "5"})

        sink = QueueSink()

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

        # Assert
        assert sink.queue.qsize() >= 10



