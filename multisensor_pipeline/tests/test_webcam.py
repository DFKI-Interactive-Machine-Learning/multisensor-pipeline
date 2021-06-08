import subprocess
import sys
import shlex
import unittest
from time import sleep

import av
import pytest
from multisensor_pipeline.tests.paths import DATA_PATH

from multisensor_pipeline.modules import QueueSink
from multisensor_pipeline.modules.video.webcam import WebCamSource
from multisensor_pipeline.pipeline.graph import GraphPipeline


@pytest.fixture()
def virtual_webcam_linux_process():
    """Start a virtual webcam using ffmpeg in a subprocess."""
    command: str = \
        'ffmpeg ' \
        '-re ' \
        '-loop 1 ' \
        f'-i {DATA_PATH / "test.png"} ' \
        '-filter:v ' \
        'format=yuv422p ' \
        '-r 30 ' \
        '-f v4l2 ' \
        '/dev/video2'
    virtual_webcam_linux_process = subprocess.Popen(
        args=shlex.split(command),
    )
    return virtual_webcam_linux_process


@pytest.fixture()
def virtual_webcam_macos_process():
    """Start a virtual webcam using ffmpeg in a subprocess."""
    command: str = \
        'ffmpeg ' \
        '-re ' \
        '-loop 1 ' \
        f'-i {DATA_PATH / "test.png"} ' \
        '-filter:v ' \
        'format=yuv422p ' \
        '-r 30 ' \
        '-f avfoundation ' \
        '/dev/video2'
    virtual_webcam_macos_process = subprocess.Popen(
        args=shlex.split(command),
    )
    return virtual_webcam_macos_process


@pytest.fixture()
def virtual_webcam_windows_process():
    """Start a virtual webcam using ffmpeg in a subprocess."""
    command: str = \
        'ffmpeg ' \
        '-re ' \
        '-loop 1 ' \
        f'-i {DATA_PATH / "test.png"} ' \
        '-filter:v ' \
        'format=yuv422p ' \
        '-r 30 ' \
        '-f dshow ' \
        '"HD WebCam"'
    print(command)
    print(shlex.split(command))
    virtual_webcam_macos_process = subprocess.Popen(
        args=shlex.split(command),
    )
    return virtual_webcam_macos_process


@pytest.mark.skipif(
    not sys.platform.startswith('darwin'),
    reason="Runs on macOS, only.",
)
# This can work on client machines, but will fail on servers.
# So attempt to run it, but allow for it to fail
@pytest.mark.xfail(strict=False)
def test_webcam_on_mac_os(virtual_webcam_macos_process):
    # (1) define the modules
    source = WebCamSource()

    sink = QueueSink()

    # (2) add module to a pipeline...
    pipeline = GraphPipeline()
    pipeline.add_source(source)
    pipeline.add_sink(sink)
    # (3) ...and connect the modules
    pipeline.connect(source, sink)

    # Test
    pipeline.start()
    sleep(2)
    pipeline.stop()

    # Assert
    assert sink.queue.qsize() > 5

    # Cleanup
    virtual_webcam_macos_process.kill()


@pytest.mark.skipif(
    not sys.platform.startswith('linux'),
    reason="Runs on Linux, only.",
)
def test_webcam_on_linux(virtual_webcam_linux_process):
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

    # Test
    pipeline.start()
    sleep(2)
    pipeline.stop()

    # Assert
    assert sink.queue.qsize() > 5

    # Cleanup
    virtual_webcam_linux_process.kill()


@pytest.mark.skipif(
    not sys.platform.startswith('win32') and
    not sys.platform.startswith('cygwin'),
    reason="Runs on Windows, only.",
)
def _test_webcam_on_windows(virtual_webcam_windows_process):
    # (1) define the modules
    source = WebCamSource(web_cam_format="vfwcap")

    sink = QueueSink()

    # (2) add module to a pipeline...
    pipeline = GraphPipeline()
    pipeline.add_source(source)
    pipeline.add_sink(sink)
    # (3) ...and connect the modules
    pipeline.connect(source, sink)

    # Test
    pipeline.start()
    sleep(2)
    pipeline.stop()

    # Assert
    assert sink.queue.qsize() > 5

    # Cleanup
    virtual_webcam_windows_process.kill()


class WebCamTesting(unittest.TestCase):
    def test_webcam_with_invalid_container_format(self):
        with pytest.raises(ValueError):
            # (1) define the modules
            _ = WebCamSource(
                web_cam_format="this_is_not_a_valid_container_format",
            )

    @pytest.mark.skipif(
        not sys.platform.startswith('linux'),
        reason="Runs on Linux, only.",
    )
    def test_webcam_with_invalid_webcam_identifier_linux(self):
        with pytest.raises(av.error.FileNotFoundError):
            # (1) define the modules
            _ = WebCamSource(
                web_cam_format="video4linux2",
                web_cam_id='this_is_not_a_valid_webcam_identifier',
            )

    @pytest.mark.skipif(
        not sys.platform.startswith('darwin'),
        reason="Runs on macOS, only.",
    )
    def test_webcam_with_invalid_webcam_identifier_mac_os(self):
        with pytest.raises(av.error.OSError):
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
    def test_webcam_with_invalid_webcam_identifier_windows_dshow(self):
        with pytest.raises(av.error.OSError):
            # (1) define the modules
            _ = WebCamSource(
                web_cam_format="dshow",
                web_cam_id='this_is_not_a_valid_webcam_identifier',
            )

    @pytest.mark.skipif(
        not sys.platform.startswith('win32') and
        not sys.platform.startswith('cygwin'),
        reason="Runs on Windows, only.",
    )
    def test_webcam_with_invalid_webcam_identifier_windows_vfwcap(self):
        with pytest.raises(av.error.OSError):
            # (1) define the modules
            _ = WebCamSource(
                web_cam_format="vfwcap",
                web_cam_id='this_is_not_a_valid_webcam_identifier',
            )
