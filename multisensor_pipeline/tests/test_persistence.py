import unittest
import numpy as np
from multisensor_pipeline.modules.persistence.recording import DefaultRecordingSink
from multisensor_pipeline.modules.persistence.replay import DefaultReplaySource
from multisensor_pipeline.modules import ListSink
from multisensor_pipeline.pipeline.graph import GraphPipeline
from multisensor_pipeline.modules.npy import RandomArraySource
from time import sleep
from PIL import Image
from multisensor_pipeline.dataframe import MSPDataFrame, Topic
import io


class DefaultSerializationTest(unittest.TestCase):

    def test_image_serialization(self):
        # create random image
        img_raw = Image.fromarray(np.random.randint(0, 255, size=(100, 100, 3)), mode="RGB")

        # simulate jpeg encoding
        buf = io.BytesIO()
        img_raw.save(buf, format="jpeg", quality=90)
        img1 = Image.open(io.BytesIO(buf.getvalue()))

        # serialize and deserialize image using the dataframe class
        frame = MSPDataFrame(data=img_raw, topic=Topic(name="image", dtype=Image.Image))
        packed = frame.serialize()
        unpacked = MSPDataFrame.deserialize(packed)
        img2 = unpacked.data

        # compare images, they should be same
        imgs_are_equal = (np.asarray(img1) == np.asarray(img2)).all()
        self.assertTrue(imgs_are_equal)

    def test_record_and_replay(self):
        filename = "recording_test.msgpack"

        # --- perform a recording ---
        # create modules
        sampling_rate = 100
        rec_source = RandomArraySource(shape=(5,), samplerate=sampling_rate)
        rec_sink = DefaultRecordingSink(filename, override=True)
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
        sleep(.1)
        rec_pipeline.stop()
        rec_pipeline.join()

        # --- load the recording ---
        # create modules
        playback_speed = 1.
        replay_source = DefaultReplaySource(file_path=filename, playback_speed=playback_speed)
        replay_list = ListSink()
        replay_pipeline = GraphPipeline()
        replay_pipeline.add_source(replay_source)
        replay_pipeline.add_sink(replay_list)
        replay_pipeline.connect(replay_source, replay_list)
        replay_pipeline.start()
        # dataset sources stop automatically
        replay_pipeline.join()

        self.assertTrue([t.timestamp for t in rec_list.list] == [t.timestamp for t in replay_list.list])
        content_check = all([(o1.data == o2.data).all() for o1, o2 in zip(rec_list.list, replay_list.list)])
        self.assertTrue(content_check)

        # --- check playback timing ---
        rec_timestamps = [t.timestamp for t in rec_list.list]
        rec_time = rec_timestamps[-1] - rec_timestamps[0]
        rec_frame_time = rec_time / (len(rec_timestamps) - 1)
        rec_fps = 1. / rec_frame_time

        # playback_timestamps = [t.playback_timestamps for t in replay_list.list]
        # playback_time = playback_timestamps[-1] - playback_timestamps[0]
        # playback_frame_time = playback_time / (len(rec_timestamps) - 1)
        # playback_fps = 1. / playback_frame_time
        #
        # mean_frame_time_diff = np.fabs(np.mean(np.diff(playback_timestamps)) - np.mean(np.diff(rec_timestamps)))
        # logging.info(
        #     f"Recording at {sampling_rate} Hz (actual: {rec_fps} Hz)\t"
        #     f"Playback ({playback_speed}x) at {playback_fps} Hz"
        # )
        # self.assertLess(float(mean_frame_time_diff), .03)
