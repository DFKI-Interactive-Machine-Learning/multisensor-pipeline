from multisensor_pipeline.dataframe import MSPDataFrame, Topic
from multisensor_pipeline.modules import BaseSink, BaseSource
from multiprocessing import Process, Value, Queue
import time


class IntSource(BaseSource):

    def __init__(self):
        super(IntSource, self).__init__()
        self._i = 0

    def _update(self) -> MSPDataFrame:
        time.sleep(.1)
        self._i += 1
        return MSPDataFrame(topic=Topic(name="int"), value=self._i)


class IntSink(BaseSink):
    def _update(self, frame: MSPDataFrame = None):
        if frame.topic.name == "int":
            print(f"[sink] received  {frame.value}")


class MPSourceWrapper(BaseSource):

    def __init__(self, module_cls, **kwargs):
        super(MPSourceWrapper, self).__init__()
        self._wrapped_active = Value("i", False)
        self._queue_out = Queue()
        self._process = Process(target=self._wrapper_worker,
                                args=(self._wrapped_active, self._queue_out, module_cls, kwargs))
        self._sinks = []

    def _start(self):
        print("[source] started")
        self._wrapped_active.value = True
        self._process.start()

    @staticmethod
    def _wrapper_worker(active, queue_out, module_cls, module_args):
        print("[source] wrapper worker started")
        module = module_cls(**module_args)
        assert isinstance(module, BaseSource)
        module.add_observer(queue_out)
        module.start()
        while active.value:
            time.sleep(.1)
        module.stop()
        print("[source] stopped")

    def _update(self) -> MSPDataFrame:
        frame = self._queue_out.get()
        print(f"[source] sent  {frame.value}")
        return frame

    def _stop(self):
        self._wrapped_active.value = False
        self._process.join()
        print("[source] ended")


class MPSinkWrapper(BaseSink):

    def __init__(self, module_cls, **kwargs):
        super(MPSinkWrapper, self).__init__()
        self._wrapped_active = Value("i", False)
        self._wrapped_queue = Queue()
        self._process = Process(target=self._wrapper_worker,
                                args=(self._wrapped_active, self._wrapped_queue, module_cls, kwargs))

    def _start(self):
        print("[sink] started")
        self._wrapped_active.value = True
        self._process.start()

    @staticmethod
    def _wrapper_worker(active, queue, module_cls, module_args):
        print("[sink] wrapper worker started")
        module = module_cls(**module_args)
        assert isinstance(module, BaseSink)

        module.start()
        while active.value:
            module.put(queue.get())
        module.stop()
        print("[sink] stopped")

    def _update(self, frame: MSPDataFrame = None):
        self._wrapped_queue.put(frame)

    def _stop(self):
        self._wrapped_active.value = False
        self._process.join()
        print("[sink] ended")


if __name__ == '__main__':
    t_start = time.perf_counter()

    # create nodes
    source = MPSourceWrapper(IntSource)
    sink = MPSinkWrapper(IntSink)

    # connect nodes
    source.add_observer(sink)

    # start nodes
    sink.start()
    source.start()
    print("Waiting for start/init to finish. We need a callback here... `await module.wait_until_started()`?")

    time.sleep(5)

    sink.stop()
    source.stop()

    t_stop = time.perf_counter()
    print(f"processing took {t_stop - t_start}s")
