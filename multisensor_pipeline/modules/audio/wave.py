from multisensor_pipeline.modules.base import BaseSink
from multisensor_pipeline.dataframe import MSPDataFrame
import wave
import pyaudio
import logging

logger = logging.getLogger(__name__)


class WaveFile(BaseSink):

    def __init__(self, filename: str, channels: int = 2, format: int = pyaudio.paInt16, rate: int = 44100):
        super(WaveFile, self).__init__()
        self._frames = []
        self._wf = wave.open(filename, 'wb')
        self._wf.setnchannels(channels)
        self._wf.setsampwidth(pyaudio.get_sample_size(format))
        self._wf.setframerate(rate)

    def on_update(self, frame: MSPDataFrame = None):
        if frame.topic.name == "audio":
            self._wf.writeframes(frame["chunk"])

    def on_stop(self):
        self._wf.close()
