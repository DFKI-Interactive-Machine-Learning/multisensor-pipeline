from multiprocessing import Process, Queue, Value
from threading import Thread
import time


class MPSource(object):

    def __init__(self):
        self._active = Value("i", False)
        self._queue_out = Queue()
        self._process = Process(target=self._worker, args=(self._active, self._queue_out))
        self._sinks = []

        self._notification_thread = Thread(target=self._notify)

    def start(self):
        print("[source] started")
        self._active.value = True
        self._notification_thread.start()
        self._process.start()

    @staticmethod
    def _start():
        print("[source] `_start` do the heavy lifting here, e.g., initializing DL models.")

    def add_observer(self, sink):
        self._sinks.append(sink)

    @staticmethod
    def _worker(active, queue_out):
        MPSource._start()
        print("[source] worker started")
        i = 0
        while active.value:
            queue_out.put(i)
            i += 1
            time.sleep(.5)

        print("[source] stopped")

    def _notify(self):
        print("[source] notification loop started")
        while self._active.value:
            msg = self._queue_out.get()
            for s in self._sinks:
                try:
                    print(f"[source] sent {msg}")
                    s.put(msg)
                except:
                    print("[source] put failed")

    def stop(self):
        self._active.value = False
        self._process.join()
        self._queue_out.put("EOF")
        self._notification_thread.join()
        print("[source] ended")


class MPSink(object):

    def __init__(self):
        self._active = Value("i", False)
        self._queue = Queue()
        self._process = Process(target=self._worker, args=(self._active, self._queue))

    def start(self):
        print("[sink] started")
        self._active.value = True
        self._process.start()

    @staticmethod
    def _start():
        print("[sink] `_start` do the heavy lifting here, e.g., initializing DL models.")

    @staticmethod
    def _worker(active, queue):
        MPSink._start()
        print("[sink] worker started")
        while active.value:
            msg = queue.get()
            print(f"[sink] received {msg}")
        print("[sink] stopped")

    def stop(self):
        self._active.value = False
        self._process.join()
        print("[sink] ended")

    def put(self, msg):
        self._queue.put(msg)


if __name__ == '__main__':
    t_start = time.perf_counter()

    # create nodes
    source = MPSource()
    sink = MPSink()

    # connect nodes
    source.add_observer(sink)

    # start nodes
    sink.start()
    source.start()
    print("Waiting for start/init to finish. We need a callback here... `await module.wait_until_started()`?")

    time.sleep(2)

    sink.stop()
    source.stop()

    t_stop = time.perf_counter()
    print(f"processing took {t_stop - t_start}s")