from time import sleep
import logging

import numpy as np

from multisensor_pipeline.modules.npy import RandomArraySource
from multisensor_pipeline.modules.persistence.recording import \
    JsonRecordingSink
from multisensor_pipeline.modules.persistence.replay import JsonReplaySource
from multisensor_pipeline.modules import ListSink
from multisensor_pipeline.pipeline.graph import GraphPipeline

logging.basicConfig(level=logging.DEBUG)


def test_record_and_replay():
    filename = "json_test.json"

    # --- perform a recording ---
    # create modules
    sampling_rate = 100
    rec_source = RandomArraySource(shape=(5,), sampling_rate=sampling_rate)
    rec_sink = JsonRecordingSink(filename, override=True)
    rec_list = ListSink()
    # add to pipeline
    rec_pipeline = GraphPipeline()
    rec_pipeline.add_source(rec_source)
    rec_pipeline.add_sink(rec_sink)
    rec_pipeline.add_sink(rec_list)
    # connect modules
    rec_pipeline.connect(rec_source, rec_sink)
    rec_pipeline.connect(rec_source, rec_list)
    # run pipeline for
    rec_pipeline.start()
    sleep(.5)
    rec_pipeline.stop()
    rec_pipeline.join()

    # --- load the recording ---
    # create modules
    playback_speed = 1.
    json_source = JsonReplaySource(
        file_path=filename,
        playback_speed=playback_speed,
    )
    json_list = ListSink()
    json_pipeline = GraphPipeline()
    json_pipeline.add_source(json_source)
    json_pipeline.add_sink(json_list)
    json_pipeline.connect(json_source, json_list)
    json_pipeline.start()
    # dataset sources stop automatically
    json_pipeline.join()

    assert \
        [t.timestamp for t in rec_list.list] == \
        [t.timestamp for t in json_list.list]

    # --- check playback timing ---
    rec_timestamps = [t.timestamp for t in rec_list.list]
    rec_time = rec_timestamps[-1] - rec_timestamps[0]
    rec_frame_time = rec_time / (len(rec_timestamps) - 1)
    rec_fps = 1. / rec_frame_time

    playback_timestamps = [t['playback_timestamp'] for t in json_list.list]
    playback_time = playback_timestamps[-1] - playback_timestamps[0]
    playback_frame_time = playback_time / (len(rec_timestamps) - 1)
    playback_fps = 1. / playback_frame_time

    mean_frame_time_diff = \
        np.fabs(
            np.mean(np.diff(playback_timestamps)) -
            np.mean(np.diff(rec_timestamps))
        )
    logging.info(
        f"Recording at {sampling_rate} Hz (actual: {rec_fps} Hz)\t"
        f"Playback ({playback_speed}x) at {playback_fps} Hz"
    )
    assert float(mean_frame_time_diff) < .03
