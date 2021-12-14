from typing import List

import numpy as np

from multisensor_pipeline.modules.base import BaseSink
from multisensor_pipeline.dataframe import MSPDataFrame, Topic
import soundfile as sf
import logging

logger = logging.getLogger(__name__)


class AudioFileSink(BaseSink):
    """
    AudioFileSink writes audio files. It supports formats that are supported by libsndfile.
    """
    def __init__(self, filename: str, channels: int = 2, samplerate: float = 44100., mode="w"):
        """
        Initialize the WaveFile Sink
        Args:
           filename: path of the audio file
           channels: Number of channels of the file
           samplerate: The audio sampling rate
           mode: w for overriding existing files,
        """
        super(AudioFileSink, self).__init__()
        self._frames = []
        self._wf = sf.SoundFile(filename, mode=mode, samplerate=int(samplerate), channels=channels)

    def on_update(self, frame: MSPDataFrame):
        self._wf.write(frame.data)

    def on_stop(self):
        """
        Stops the AudioFileSink and closes the filestream
        """
        self._wf.close()

    @property
    def input_topics(self) -> List[Topic]:
        return [Topic(name="audio", dtype=np.ndarray)]

