from multisensor_pipeline.modules.audio.microphone import Microphone
import wave
import pyaudio
from queue import Queue
import logging

if __name__ == '__main__':

    queue = Queue()
    chunks = []

    try:
        mic = Microphone(channels=2)
        mic.add_observer(queue)
        mic.start()

        for i in range(500):
            frame = queue.get()
            chunks.append(frame["chunk"])

    except Exception as e:
        logging.error(e)
    finally:
        mic.stop()

    wf = wave.open('test.wav', 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
    wf.setframerate(44100)
    wf.writeframes(b''.join(chunks))
    wf.close()
