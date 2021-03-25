from unittest import TestCase
from multisensor_pipeline.pipeline import GraphPipeline
from time import sleep
from multisensor_pipeline.modules.npy import RandomArraySource
from multisensor_pipeline.modules.recording import JsonRecordingSink
from multisensor_pipeline.modules.dataset import JsonDatasetSource
from multisensor_pipeline.modules import QueueSink


class JsonSerializationTest(TestCase):

    def test_pipeline(self):
        filename = "json_test.json"

        # --- perform a recording ---
        # create modules
        rec_source = RandomArraySource(shape=(50,), frequency=50)
        rec_sink = JsonRecordingSink(filename, override=True)
        rec_queue = QueueSink()
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
        sleep(.1)
        rec_pipeline.stop()

        # --- load the recording ---
        # create modules
        json_source = JsonDatasetSource(file_path=filename)
        json_queue = QueueSink()
        json_pipeline = GraphPipeline()
        json_pipeline.add_source(json_source)
        json_pipeline.add_sink(json_queue)
        json_pipeline.connect(json_source, json_queue)
        json_pipeline.start()
        sleep(.1)  # TODO: use autostop with a callback instead.
        json_pipeline.stop()

        # TODO: compare queue contents
        self.assertTrue(False)
