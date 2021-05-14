import sys
from time import sleep

import pytest

from multisensor_pipeline.modules import QueueSink
from multisensor_pipeline.modules.video.webcam import WebCamSource
from multisensor_pipeline.pipeline.graph import GraphPipeline


def test_no_webcam():
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
    except ValueError:
        assert True


@pytest.mark.skipif(
    not sys.platform.startswith('darwin'),
    reason="Runs on MacOS, only.",
)
def test_mac_webcam():
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
    assert sink.queue.qsize() > 5


@pytest.mark.skipif(
    not sys.platform.startswith('linux'),
    reason="Runs on Linux, only.",
)
def test_linux_webcam():
    # (1) define the modules
    webcam_source = WebCamSource(
        web_cam_format="video4linux2",
        web_cam_id="/dev/video2",
        options={
            'framerate': '30',
        }
    )

    sink = QueueSink()

    # (2) add module to a pipeline...
    pipeline = GraphPipeline()
    pipeline.add_source(webcam_source)
    pipeline.add_sink(sink)
    # (3) ...and connect the modules
    pipeline.connect(webcam_source, sink)

    pipeline.start()
    sleep(2)
    pipeline.stop()
    assert sink.queue.qsize() > 5


@pytest.mark.skipif(
    not sys.platform.startswith('win32') and
    not sys.platform.startswith('cygwin'),
    reason="Runs on Windows, only.",
)
def test_win_webcam():
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
    assert sink.queue.qsize() > 5
