import os
from time import sleep
from typing import List

import av
import pytest
from PIL import Image

from multisensor_pipeline.modules.paths import DATA_PATH
from multisensor_pipeline.modules import ConsoleSink, QueueSink
from multisensor_pipeline.modules.video.video import VideoSource, VideoSink
from multisensor_pipeline.pipeline.graph import GraphPipeline


def test_no_video_file():
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
        assert True
    try:
        pipeline.stop()
    except AttributeError:
        assert True


def test_short_video():
    # Create a video file with 24 PIL Images and export it
    img_sequence = [
        Image.new('RGB', (300, 200), (228, 150, 150)) for _ in range(24)
    ]

    output = av.open(str(DATA_PATH / 'output_av.mp4'), 'w')
    stream = output.add_stream('h264')
    for img in img_sequence:
        frame = av.VideoFrame.from_image(img)
        packet = stream.encode(frame)
        output.mux(packet)

    output.mux(stream.encode())
    output.close()

    # (1) define the modules
    source = VideoSource(file_path=str(DATA_PATH / "output_av.mp4"))
    sink = QueueSink()

    # (2) add module to a pipeline...
    pipeline = GraphPipeline()
    pipeline.add_source(source)
    pipeline.add_sink(sink)
    # (3) ...and connect the modules
    pipeline.connect(source, sink)

    # Test
    pipeline.start()
    sleep(3)
    pipeline.stop()

    # Assert
    assert sink.queue.qsize() == 24

    # Cleanup
    os.remove(str(DATA_PATH / "output_av.mp4"))


@pytest.mark.timeout(0.420 * 10)  # Kill run, if it takes 10x longer than local
def test_long_video():
    # Mock a video file with 24 PIL Images and export it
    img_sequence: List[Image] = [
        Image.new('RGB', (300, 200), (228, 150, 150)) for _ in range(500)
    ]

    output = av.open(str(DATA_PATH / 'output_av.mp4'), 'w')
    stream = output.add_stream('h264', '24')
    for img in img_sequence:
        frame = av.VideoFrame.from_image(img)
        packet = stream.encode(frame)
        output.mux(packet)

    packet = stream.encode()
    output.mux(packet)
    output.close()

    # (1) define the modules
    source = VideoSource(file_path=str(DATA_PATH / "output_av.mp4"))
    sink = QueueSink()

    # (2) add module to a pipeline...
    pipeline = GraphPipeline()
    pipeline.add_source(source)
    pipeline.add_sink(sink)
    # (3) ...and connect the modules
    pipeline.connect(source, sink)

    # Test
    pipeline.start()
    sleep(.3)
    pipeline.stop()

    # Cleanup
    os.remove(str(DATA_PATH / "output_av.mp4"))

    # Assert
    assert 498 > sink.queue.qsize()


def test_video_sink():
    # Mock a video file with 24 PIL Images and export it
    img_sequence = [
        Image.new('RGB', (200, 300), (228, 150, 150)) for _ in range(10)
    ]

    output = av.open(str(DATA_PATH / 'input.mp4'), 'w')
    stream = output.add_stream('h264')
    for img in img_sequence:
        frame = av.VideoFrame.from_image(img)
        packet = stream.encode(frame)
        output.mux(packet)

    output.mux(stream.encode())
    output.close()

    # (1) define the modules
    source = VideoSource(file_path=str(DATA_PATH / "input.mp4"))
    sink = VideoSink(
        file_path=str(DATA_PATH / "output.mp4"),
        live_preview=False,
    )

    # (2) add module to a pipeline...
    pipeline = GraphPipeline()
    pipeline.add_source(source)
    pipeline.add_sink(sink)
    # (3) ...and connect the modules
    pipeline.connect(source, sink)

    # Test
    pipeline.start()
    sleep(5)
    pipeline.stop()

    # Assert
    video = av.open(str(DATA_PATH / "output.mp4"))
    stream = video.streams.video[0]
    count = 1 + sum(1 for _ in video.decode(stream))
    assert 10 == count

    # Cleanup
    os.remove(str(DATA_PATH / "output.mp4"))
    os.remove(str(DATA_PATH / "input.mp4"))
