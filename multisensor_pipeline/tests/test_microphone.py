import logging
from time import sleep

from multisensor_pipeline.modules import ListSink
from multisensor_pipeline.modules.audio.microphone import Microphone


def _test_microphone_input():
    sink = ListSink()
    try:
        mic = Microphone(channels=1)
        mic.add_observer(sink)
        sink.start()
        mic.start()
        logging.info("recording started")
        sleep(.2)
    except Exception as e:
        logging.error(e)
    finally:
        mic.stop(blocking=False)
        sink.join()
        logging.info("recording stopped")

    chunks = [f["chunk"] for f in sink.list]

    assert len(chunks) > 0
