from time import sleep
import pathlib

from multisensor_pipeline.modules.audio.microphone import Microphone
from multisensor_pipeline.modules.audio.wave import WaveFile
from multisensor_pipeline.pipeline.graph import GraphPipeline


def _test_mic_to_wave_pipeline():
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
