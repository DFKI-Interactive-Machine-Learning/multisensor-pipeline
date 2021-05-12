from typing import Optional
import pyaudio
import logging

from multisensor_pipeline.dataframe.dataframe import MSPDataFrame
from multisensor_pipeline.modules.base.base import BaseSource

logger = logging.getLogger(__name__)


class Microphone(BaseSource):
    """Microphone Source for live audio recording of a connected microphone."""

    def __init__(
        self,
        device: str,
        format=pyaudio.paInt16,
        channels: int = 2,
        sampling_rate: int = 44100,
        chunk_size: int = 1024,
    ):
        """
        Initialize the Source.

        Args:
           device: Device id of the microphone
           format: PyAudio format specification
           channels: Number of channels of the device
           sampling_rate: The audio sampling rate
           chunk_size: Size of the chunks of the recordings
        """
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

    def on_update(self) -> Optional[MSPDataFrame]:
        """Send chunks of the audio recording."""
        data = self._stream.read(self.chunk_size)
        return MSPDataFrame(
            topic=self._generate_topic(name="audio"),
            chunk=data,
        )

    def on_stop(self):
        """Stop the Microphone source and close the stream."""
        self._stream.stop_stream()
        self._stream.close()
        self._mic.terminate()
