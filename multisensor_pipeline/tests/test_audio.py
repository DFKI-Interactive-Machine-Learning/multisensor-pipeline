import os
import unittest
from time import sleep
import pathlib

from multisensor_pipeline.dataframe import Topic
from multisensor_pipeline.modules import ListSink
from multisensor_pipeline.modules.audio.microphone import MicrophoneSource
from multisensor_pipeline.modules.audio.wave import WaveFileSink
from multisensor_pipeline.pipeline.graph import GraphPipeline


class AudioTest(unittest.TestCase):
    _filename = 'test_mic_to_wave_pipeline.wav'

    @staticmethod
    def _run_simple_mic_pipeline(topic=None):
        # create nodes
        mic = MicrophoneSource(channels=1)
        list = ListSink()

        # add and connect nodes
        pipeline = GraphPipeline()
        pipeline.add_source(mic)
        pipeline.add_sink(list)
        pipeline.connect(mic, list, topics=topic)

        # start pipeline
        pipeline.start()
        sleep(1.)
        pipeline.stop()
        pipeline.join()
        return list

    @staticmethod
    def _run_mic_to_wave_pipeline(filename='test_mic_to_wave_pipeline.wav', topic=None):
        # create nodes
        mic = MicrophoneSource(channels=1)
        wav = WaveFileSink(filename, channels=1)

        # add and connect nodes
        pipeline = GraphPipeline()
        pipeline.add_source(mic)
        pipeline.add_sink(wav)
        pipeline.connect(mic, wav, topics=topic)

        # start pipeline
        pipeline.start()
        sleep(1.)
        pipeline.stop()
        pipeline.join()

    def test_mic_simple(self):
        sink = self._run_simple_mic_pipeline()
        self.assertGreater(len(sink), 1)

    def test_mic_simple_topic_filtered(self):
        sink = self._run_simple_mic_pipeline(topic=Topic(name="audio", dtype=bytes))
        self.assertGreater(len(sink), 1)

    def test_mic_to_wave_pipeline(self):
        self._run_mic_to_wave_pipeline(filename=self._filename)
        wav_file = pathlib.Path(self._filename)
        self.assertTrue(wav_file.exists())
        self.assertTrue(wav_file.is_file())
        # Cleanup
        os.remove(self._filename)


    def test_mic_to_wave_pipeline_topic_filtered(self):
        self._run_mic_to_wave_pipeline(topic=Topic(name="audio", dtype=bytes), filename=self._filename)
        wav_file = pathlib.Path(self._filename)
        self.assertTrue(wav_file.exists())
        self.assertTrue(wav_file.is_file())
        # Cleanup
        os.remove(self._filename)
