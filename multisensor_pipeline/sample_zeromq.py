from multisensor_pipeline.modules.network import ZmqPublisher, ZmqSubscriber
from multisensor_pipeline.modules.audio.microphone import Microphone
from multisensor_pipeline.modules.audio.wave import WaveFile
from multisensor_pipeline.pipeline import LinearPipeline
import pyaudio
from time import sleep
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

CHUNK = 1024
RATE = 44100
CHANNELS = 1
FORMAT = pyaudio.paInt16
RECORD_SEC = 10


if __name__ == '__main__':
    logger.info("initialize pipelines: [mic -> pub] ->TCP-> [sub -> final_sink].")

    # initialize audio subscriber pipeline
    sub_pipeline = LinearPipeline()
    sub_pipeline.append(ZmqSubscriber())
    sub_pipeline.append(WaveFile('test.wav', channels=CHANNELS, format=FORMAT, rate=RATE))

    # initialize audio publisher pipeline
    pub_pipeline = LinearPipeline()
    pub_pipeline.append(Microphone(format=FORMAT, channels=CHANNELS, sampling_rate=RATE, chunk_size=CHUNK))
    pub_pipeline.append(ZmqPublisher())

    logger.info("start pipelines in forward order.")
    pub_pipeline.start()
    sub_pipeline.start()

    logger.info("recording for {}s.".format(RECORD_SEC))
    sleep(RECORD_SEC)

    logger.info("stop pipelines in reverse order.")
    sub_pipeline.stop()
    pub_pipeline.stop()
