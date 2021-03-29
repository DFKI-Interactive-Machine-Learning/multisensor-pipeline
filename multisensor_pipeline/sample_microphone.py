from multisensor_pipeline.modules.audio.microphone import Microphone
from multisensor_pipeline.modules import ListSink
import wave
import pyaudio
import logging
from time import sleep
import logging


logging.basicConfig(level=logging.DEBUG)


if __name__ == '__main__':
    n_channels = 2

    sink = ListSink()
    try:
        mic = Microphone(channels=n_channels)
        mic.add_observer(sink)
        sink.start()
        mic.start()
        logging.info("recording started")
        sleep(5)
    except Exception as e:
        logging.error(e)
    finally:
        mic.stop(blocking=False)
        sink.join()
        logging.info("recording stopped")

    chunks = [f["chunk"] for f in sink.list]

    wf = wave.open('test.wav', 'wb')
    wf.setnchannels(n_channels)
    wf.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
    wf.setframerate(44100)
    wf.writeframes(b''.join(chunks))
    wf.close()
