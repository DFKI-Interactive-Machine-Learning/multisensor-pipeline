import ray
import time
from ray.util.queue import Queue as RayQueue

ray.init()


@ray.remote
class RaySource(object):

    _active = False
    _sinks = []

    def start(self):
        print("started source")
        self._active = True
        self._worker()
        print("stopped source")
        return True

    def add_observer(self, sink):
        self._sinks.append(sink)

    def _worker(self):
        i = 0
        while self._active:
            self._notify(i)
            i += 1
            time.sleep(.5)

    def _notify(self, msg):
        for s in self._sinks:
            print(f"sent {msg}")
            s.put.remote(msg)

    def stop(self):
        self._active = False


@ray.remote
class RaySink(object):

    def __init__(self):
        self._active = False
        self._ray_queue = RayQueue()

    def start(self):
        print("started sink")
        self._active = True
        self._worker()
        print("stopped sink")
        return True

    def _worker(self):
        while self._active:
            msg = self._ray_queue.get()
            print(f"received {msg}")

    def stop(self):
        self._active = False

    def put(self, msg):
        self._ray_queue.put(msg)


def main():
    t_start = time.perf_counter()

    # create nodes
    source = RaySource.options(max_concurrency=2).remote()
    sink = RaySink.options(max_concurrency=2).remote()

    # connect nodes
    source.add_observer.remote(sink)

    # start nodes
    sink_ret = sink.start.remote()
    source_ret = source.start.remote()

    time.sleep(60)

    source.stop.remote()
    assert ray.get(source_ret)
    sink.stop.remote()
    sink.put.remote("stop")
    assert ray.get(sink_ret)

    t_stop = time.perf_counter()
    print(f"processing took {t_stop - t_start}s")


if __name__ == '__main__':
    main()
