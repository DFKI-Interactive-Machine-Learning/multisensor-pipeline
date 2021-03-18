from multisensor_pipeline.modules.base import BaseSource
import pyaudio
import logging

logger = logging.getLogger(__name__)


class Microphone(BaseSource):

    def __init__(self, device=None, format=pyaudio.paInt16, channels=2, sampling_rate=44100, chunk_size=1024):
        super(Microphone, self).__init__()

        self.device = device
        self.format = format
        self.channels = channels
        self.sampling_rate = sampling_rate
        self.chunk_size = chunk_size

        self._mic = pyaudio.PyAudio()
        self._stream = self._mic.open(format=self.format,
                                      channels=self.channels,
                                      rate=self.sampling_rate,
                                      input=True,
                                      frames_per_buffer=self.chunk_size)

    def _update(self, frame=None):
        while self._active:
            data = self._stream.read(self.chunk_size)
            self._notify('microphone', data)

    def _stop(self):
        self._stream.stop_stream()
        self._stream.close()
        self._mic.terminate()
