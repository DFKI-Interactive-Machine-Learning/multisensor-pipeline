from unittest import TestCase
from multisensor_pipeline.pipeline import GraphPipeline
from time import sleep, time
from multisensor_pipeline.modules.npy import RandomArraySource
from multisensor_pipeline.modules.persitence.recording import JsonRecordingSink
from multisensor_pipeline.modules.persitence.dataset import JsonDatasetSource
from multisensor_pipeline.modules import ListSink
import numpy as np


class JsonSerializationTest(TestCase):

    def test_rec_and_replay(self):
        filename = "json_test.json"

        # --- perform a recording ---
        # create modules
        rec_source = RandomArraySource(shape=(5,), sampling_rate=100)
        rec_sink = JsonRecordingSink(filename, override=True)
        rec_queue = ListSink()
        # add to pipeline
        rec_pipeline = GraphPipeline()
        rec_pipeline.add_source(rec_source)
        rec_pipeline.add_sink(rec_sink)
        rec_pipeline.add_sink(rec_queue)
        # connect modules
        rec_pipeline.connect(rec_source, rec_sink)
        rec_pipeline.connect(rec_source, rec_queue)
        # run pipeline for
        rec_pipeline.start()
        sleep(.5)
        rec_pipeline.stop()
        rec_pipeline.join()

        # --- load the recording ---
        # create modules
        json_source = JsonDatasetSource(file_path=filename, playback_speed=1.)
        json_queue = ListSink()
        json_pipeline = GraphPipeline()
        json_pipeline.add_source(json_source)
        json_pipeline.add_sink(json_queue)
        json_pipeline.connect(json_source, json_queue)
        json_pipeline.start()
        # dataset sources stop automatically
        json_pipeline.join()

        self.assertTrue([t.timestamp for t in rec_queue.list] == [t.timestamp for t in json_queue.list])

        # --- check playback timing ---
        rec_timestamps = [t.timestamp for t in rec_queue.list]
        rec_time = rec_timestamps[-1] - rec_timestamps[0]
        rec_frame_time = rec_time / (len(rec_timestamps) - 1)
        rec_fps = 1. / rec_frame_time

        playback_timestamps = [t['playback_timestamp'] for t in json_queue.list]
        playback_time = playback_timestamps[-1] - playback_timestamps[0]
        plaback_frame_time = playback_time / (len(rec_timestamps) - 1)
        playback_fps = 1. / plaback_frame_time

        mean_frame_time_diff = np.fabs(np.mean(np.diff(playback_timestamps)) - np.mean(np.diff(rec_timestamps)))
        self.assertLess(float(mean_frame_time_diff), .03)
