from multisensor_pipeline.modules.base import BaseSink
import wave
import pyaudio
import logging

logger = logging.getLogger(__name__)


class WaveFile(BaseSink):

    def __init__(self, filename, channels, format, rate):
        super(WaveFile, self).__init__()
        self._frames = []
        self._wf = wave.open(filename, 'wb')
        self._wf.setnchannels(channels)
        self._wf.setsampwidth(pyaudio.get_sample_size(format))
        self._wf.setframerate(rate)

    def _update_loop(self):
        while self._active:
            _, data = self.get()
            self._wf.writeframes(data["data"])

    def _stop(self):
        self._wf.close()
