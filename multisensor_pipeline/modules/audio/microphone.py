from multisensor_pipeline.modules.base import BaseSource
from multisensor_pipeline.dataframe import MSPDataFrame, Topic
from typing import Optional, List
import pyaudio
import logging

logger = logging.getLogger(__name__)


class MicrophoneSource(BaseSource):
    """
    Microphone Source for live audio recording of a connected microphone
    """

    def __init__(self, device: str = "", pyaudio_format=pyaudio.paInt16, channels: int = 2, sampling_rate: int = 44100,
                 chunk_size: int = 1024):
        """
        Initialize the Source
        Args:
           device: Device id of the microphone
           format: PyAudio format specification
           channels: Number of channels of the device
           sampling_rate: The audio sampling rate
           chunk_size: Size of the chunks of the recordings
        """
        super(MicrophoneSource, self).__init__()

        self.device = device
        self.pyaudio_format = pyaudio_format
        self.channels = channels
        self.sampling_rate = sampling_rate
        self.chunk_size = chunk_size

        self._mic = pyaudio.PyAudio()
        self._stream = self._mic.open(format=self.pyaudio_format,
                                      channels=self.channels,
                                      rate=self.sampling_rate,
                                      input=True,
                                      frames_per_buffer=self.chunk_size)

    def on_update(self) -> Optional[MSPDataFrame]:
        """
        Sends chunks of the audio recording
        """
        data = self._stream.read(self.chunk_size)
        return MSPDataFrame(topic=self.output_topics[0], data=data)

    def on_stop(self):
        """
        Stops the Microphone source and closes the stream
        """
        self._stream.stop_stream()
        self._stream.close()
        self._mic.terminate()

    @property
    def output_topics(self) -> Optional[List[Topic]]:
        return [Topic(name="audio", dtype=bytes)]

