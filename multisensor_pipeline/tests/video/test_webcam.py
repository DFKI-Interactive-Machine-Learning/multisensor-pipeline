import sys
from time import sleep

import av
import pytest

from multisensor_pipeline.modules import QueueSink
from multisensor_pipeline.modules.video.webcam import WebCamSource
from multisensor_pipeline.pipeline.graph import GraphPipeline


def test_webcam_with_invalid_container_format():
    with pytest.raises(ValueError):
        # (1) define the modules
        _ = WebCamSource(
            web_cam_format="this_is_not_a_valid_container_format",
        )


@pytest.mark.skipif(
    not sys.platform.startswith('linux'),
    reason="Runs on Linux, only.",
)
def test_webcam_with_invalid_webcam_identifier_linux():
    with pytest.raises(av.error.FileNotFoundError):
        # (1) define the modules
        _ = WebCamSource(
            web_cam_format="video4linux2",
            web_cam_id='this_is_not_a_valid_webcam_identifier',
        )


@pytest.mark.skipif(
    not sys.platform.startswith('darwin'),
    reason="Runs on MacOS, only.",
)
def test_webcam_with_invalid_webcam_identifier_mac_os():
    with pytest.raises(av.error.FileNotFoundError):
        # (1) define the modules
        _ = WebCamSource(
            web_cam_format="avfoundation",
            web_cam_id='this_is_not_a_valid_webcam_identifier',
        )


@pytest.mark.skipif(
    not sys.platform.startswith('win32') and
    not sys.platform.startswith('cygwin'),
    reason="Runs on Windows, only.",
)
def test_webcam_with_invalid_webcam_identifier_windows():
    with pytest.raises(av.error.FileNotFoundError):
        # (1) define the modules
        _ = WebCamSource(
            web_cam_format="vfwcap",
            web_cam_id='this_is_not_a_valid_webcam_identifier',
        )


@pytest.mark.skipif(
    not sys.platform.startswith('darwin'),
    reason="Runs on MacOS, only.",
)
def test_webcam_on_mac_os():
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
def test_webcam_on_linux():
    # (1) define the modules
    webcam_source = None
    webcam_identifiers = (
        '/dev/video0',
        '/dev/video1',
        '/dev/video2',
    )
    for webcam_identifier in webcam_identifiers:
        try:
            webcam_source = WebCamSource(
                web_cam_format="video4linux2",
                web_cam_id=webcam_identifier,
                options={
                    'framerate': '30',
                }
            )
        except (av.error.FileNotFoundError, av.error.OSError):
            pass
    if webcam_source is None:
        print(
            f'Could not find a webcam under Linux. '
            f'Tried: {webcam_identifiers} '
            f'Thus, skipping this test. '
            f'Test coverage may be reduced.'
        )
        return

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
def test_webcam_on_windows():
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
