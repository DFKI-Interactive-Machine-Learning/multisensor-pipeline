import logging
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

    def test_mic_simple(self):
        pipeline = self.mic_simple()
        for sink in pipeline.sink_nodes:
            assert len(sink.list) > 1

    def test_mic_simple_topic_filtered(self):
        pipeline = self.mic_simple(topic=Topic(name="audio", dtype=bytes))
        for sink in pipeline.sink_nodes:
            assert len(sink.list) > 1

    def mic_simple(self, topic=None):
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
        sleep(2)
        pipeline.stop()
        pipeline.join()
        return pipeline

    def test_mic_to_wave_pipeline(self):
        self.mic_to_wave_pipeline()
        assert pathlib.Path(self._filename).exists()
        assert pathlib.Path(self._filename).is_file()
        # Cleanup
        os.remove(self._filename)

    def test_mic_to_wave_pipeline_topic_filtered(self):
        self.mic_to_wave_pipeline(topic=Topic(name="audio", dtype=bytes))
        assert os.path.exists(self._filename)
        assert os.path.isfile(self._filename)
        # Cleanup
        os.remove(self._filename)

    def mic_to_wave_pipeline(self, topic=None):
        # create nodes
        mic = MicrophoneSource(channels=1)
        wav = WaveFileSink(self._filename, channels=1)

        # add and connect nodes
        pipeline = GraphPipeline()
        pipeline.add_source(mic)
        pipeline.add_sink(wav)
        pipeline.connect(mic, wav, topics=topic)

        # start pipeline
        pipeline.start()
        sleep(2)
        pipeline.stop()
        pipeline.join()
