from multisensor_pipeline.modules.base import BaseSource
from multisensor_pipeline.dataframe import MSPDataFrame, Topic
from typing import Optional, List
import sounddevice as sd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class MicrophoneSource(BaseSource):
    """
    Microphone Source for live audio recording of a connected microphone
    """

    class InputDevice:

        def __init__(self, device_info: dict):
            self._device_info = device_info

        @property
        def name(self) -> str:
            return self._device_info["name"]

        @property
        def channels(self) -> int:
            return self._device_info["max_input_channels"]

        @property
        def default_samplerate(self) -> float:
            return self._device_info["default_samplerate"]

        @property
        def device_info(self) -> dict:
            return self._device_info

        def __str__(self):
            return f"[{self.name}; channels={self.channels}; rate={self.default_samplerate}"

    @staticmethod
    def available_input_devices():
        devices = sd.query_devices()
        return [MicrophoneSource.InputDevice(d) for d in devices if d["max_input_channels"] > 0]

    def __init__(self, device: Optional[InputDevice] = None,
                 channels: Optional[int] = None,
                 samplerate: Optional[float] = None,
                 blocksize: Optional[int] = 1024):
        """
        Initialize the Source
        Args:
           device: Device id of the microphone
           channels: Number of channels of the device
           samplerate: The audio sampling rate
           blocksize: Size of the chunks of the recordings
        """
        super(MicrophoneSource, self).__init__()

        if device is None:
            device = MicrophoneSource.InputDevice(sd.query_devices(kind='input'))
        self._device = device
        self._samplerate = self._device.default_samplerate if samplerate is None else samplerate
        self._channels = self._device.channels if channels is None else channels
        self._blocksize = blocksize
        self._stream = sd.InputStream(
            samplerate=self._samplerate,
            blocksize=self._blocksize,
            device=self._device.name,
            channels=self._channels
        )

    def on_start(self):
        self._stream.start()

    def on_update(self) -> Optional[MSPDataFrame]:
        """
        Sends chunks of the audio recording
        """
        t = self._stream.time
        data, _ = self._stream.read(self._blocksize)
        return MSPDataFrame(topic=self.output_topics[0], data=data.copy(), timestamp=t)

    def on_stop(self):
        """
        Stops the Microphone source and closes the stream
        """
        self._stream.close()

    @property
    def device(self) -> InputDevice:
        return self._device

    @property
    def channels(self) -> int:
        return self._channels

    @property
    def samplerate(self) -> float:
        return self._samplerate

    @property
    def output_topics(self) -> Optional[List[Topic]]:
        return [Topic(name="audio", dtype=np.ndarray)]
