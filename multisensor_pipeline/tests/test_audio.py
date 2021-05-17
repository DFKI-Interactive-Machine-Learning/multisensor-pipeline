import logging
import unittest
from time import sleep
import pathlib

from multisensor_pipeline.modules import ListSink
from multisensor_pipeline.modules.audio.microphone import Microphone
from multisensor_pipeline.modules.audio.wave import WaveFile
from multisensor_pipeline.pipeline.graph import GraphPipeline


class AudioTest(unittest.TestCase):

    def _test_microphone_input(self):
        sink = ListSink()
        try:
            mic = Microphone(channels=1)
            mic.add_observer(sink)
            sink.start()
            mic.start()
            logging.info("recording started")
            sleep(.2)
        except Exception as e:
            logging.error(e)
        finally:
            mic.stop(blocking=False)
            sink.join()
            logging.info("recording stopped")

        chunks = [f["chunk"] for f in sink.list]

        assert len(chunks) > 0

    def _test_mic_to_wave_pipeline(self):
        filename = 'test_mic_to_wave_pipeline.wav'

        # create nodes
        mic = Microphone(channels=1)
        wav = WaveFile(filename, channels=1)

        # add and connect nodes
        pipeline = GraphPipeline()
        pipeline.add_source(mic)
        pipeline.add_sink(wav)
        pipeline.connect(mic, wav)

        # start pipeline
        pipeline.start()
        sleep(2)
        pipeline.stop()
        pipeline.join()

        assert pathlib.Path(filename).exists()
        assert pathlib.Path(filename).is_file()
