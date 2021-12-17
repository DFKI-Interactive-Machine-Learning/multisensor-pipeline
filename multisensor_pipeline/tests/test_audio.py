import os
import unittest
from time import sleep
import pathlib

import numpy as np

from multisensor_pipeline.dataframe import Topic
from multisensor_pipeline.modules import ListSink
from multisensor_pipeline.modules.audio.microphone import MicrophoneSource
from multisensor_pipeline.modules.audio.file import AudioFileSink
from multisensor_pipeline.pipeline.graph import GraphPipeline


class AudioTest(unittest.TestCase):

    @staticmethod
    def _run_simple_mic_pipeline(topic=None):
        # create nodes
        mic = MicrophoneSource()
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
        mic = MicrophoneSource()
        wav = AudioFileSink(filename, channels=mic.channels, samplerate=mic.samplerate)

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

    def _est_mic_simple(self):
        sink = self._run_simple_mic_pipeline()
        # import soundfile as sf
        # with sf.SoundFile("test.flac", mode="w", samplerate=44100, channels=1) as sfile:
        #     for frame in sink.list:
        #         sfile.write(frame.data)
        self.assertGreater(len(sink), 1)

    def _test_mic_simple_topic_filtered(self):
        sink = self._run_simple_mic_pipeline(topic=Topic(name="audio", dtype=np.ndarray))
        self.assertGreater(len(sink), 1)

    def _test_mic_to_wave_pipeline(self):
        filename = 'test_mic_to_wave_pipeline_01.wav'
        self._run_mic_to_wave_pipeline(filename=filename)
        wav_file = pathlib.Path(filename)
        self.assertTrue(wav_file.exists())
        self.assertTrue(wav_file.is_file())
        # Cleanup
        os.remove(filename)

    def _test_mic_to_wave_pipeline_topic_filtered(self):
        filename = 'test_mic_to_wave_pipeline_02.wav'
        self._run_mic_to_wave_pipeline(topic=Topic(name="audio", dtype=np.ndarray), filename=filename)
        wav_file = pathlib.Path(filename)
        self.assertTrue(wav_file.exists())
        self.assertTrue(wav_file.is_file())
        # Cleanup
        os.remove(filename)
