import wave
import pyaudio
import logging

from multisensor_pipeline.dataframe.dataframe import MSPDataFrame
from multisensor_pipeline.modules import BaseSink

logger = logging.getLogger(__name__)


class WaveFile(BaseSink):
    """WaveFile Sink for .wav files."""

    def __init__(
        self,
        filename: str,
        channels: int = 2,
        format: int = pyaudio.paInt16,
        rate: int = 44100,
    ):
        """
        Initialize the WaveFile Sink.

        Args:
           filename: path of the wav file
           channels: Number of channels of the file
           format: PyAudio format specification
           rate: The audio sampling rate
        """
        super(WaveFile, self).__init__()
        self._frames = []
        self._wf = wave.open(filename, 'wb')
        self._wf.setnchannels(channels)
        self._wf.setsampwidth(pyaudio.get_sample_size(format))
        self._wf.setframerate(rate)

    def on_update(self, frame: MSPDataFrame):
        """Write chunks of the .wav file."""
        if frame.topic.name == "audio":
            self._wf.writeframes(frame["chunk"])

    def on_stop(self):
        """Stop the WaveFileSink and closes the filestream."""
        self._wf.close()
