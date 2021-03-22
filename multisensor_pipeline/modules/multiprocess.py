from abc import ABC, abstractmethod
from multisensor_pipeline.dataframe import MSPDataFrame, Topic
from multisensor_pipeline.modules.base import BaseSink, BaseSource, BaseModule, BaseProcessor
from multiprocessing import Process, Value, Queue
import multiprocessing as mp
import logging
import time

logger = logging.getLogger(__name__)


class MultiprocessModuleWrapper(BaseModule, ABC):

    def __init__(self, module_cls: type, **module_args):
        super(MultiprocessModuleWrapper, self).__init__()

        self._wrapped_module_cls = module_cls
        self._wrapped_module_args = module_args

        self._process_active = Value("i", False)
        self._process = self._init_process()

    @abstractmethod
    def _init_process(self) -> Process:
        raise NotImplementedError()

    def _start(self):
        self._process_active.value = True
        self._process.start()

    @staticmethod
    @abstractmethod
    def _process_worker(module_cls: type, module_args: dict, active, queue: mp.queues.Queue):
        raise NotImplementedError()

    def _stop(self):
        self._process_active.value = False
        self._process.join()


class MultiprocessSourceWrapper(MultiprocessModuleWrapper, BaseSource):

    def _init_process(self) -> Process:
        self._queue_out = Queue()
        return Process(target=self._process_worker,
                       args=(self._wrapped_module_cls, self._wrapped_module_args,
                             self._process_active, self._queue_out))

    @staticmethod
    def _process_worker(module_cls: type, module_args: dict, active, queue_out: mp.queues.Queue):
        # TODO: This part is redundant
        # TODO: this should be done before the pipeline actually starts -> do we need an additional lifecycle stage?
        module = module_cls(**module_args)
        assert isinstance(module, BaseSource)
        # TODO: wait here until start() was called for the wrapper module

        module.add_observer(queue_out)
        module.start()
        while active.value:
            time.sleep(.1)
        module.stop()

    def _update(self) -> MSPDataFrame:
        return self._queue_out.get()


class MultiprocessSinkWrapper(MultiprocessModuleWrapper, BaseSink):

    def _init_process(self) -> Process:
        self._queue_in = Queue()
        return Process(target=self._process_worker,
                       args=(self._wrapped_module_cls, self._wrapped_module_args,
                             self._process_active, self._queue_in))

    @staticmethod
    def _process_worker(module_cls: type, module_args: dict, active, queue_in: mp.queues.Queue):
        # TODO: This part is redundant
        # TODO: this should be done before the pipeline actually starts -> do we need an additional lifecycle stage?
        module = module_cls(**module_args)
        assert isinstance(module, BaseSink)
        # TODO: wait here until start() was called for the wrapper module

        module.start()
        while active.value:
            module.put(queue_in.get())
        module.stop()

    def _update(self, frame: MSPDataFrame = None):
        self._queue_in.put(frame)


class MultiprocessProcessorWrapper(MultiprocessModuleWrapper, BaseProcessor):

    def _init_process(self) -> Process:
        self._queue_in = Queue()
        self._queue_out = Queue()
        return Process(target=self._process_worker,
                       args=(self._wrapped_module_cls, self._wrapped_module_args,
                             self._process_active, self._queue_in, self._queue_out))

    def _update(self, frame: MSPDataFrame = None):
        self._queue_in.put(frame)
        self._notify(self._queue_out.get())

    @staticmethod
    def _process_worker(module_cls: type, module_args: dict, active,
                        queue_in: mp.queues.Queue, queue_out: mp.queues.Queue):
        # TODO: This part is redundant
        # TODO: this should be done before the pipeline actually starts -> do we need an additional lifecycle stage?
        module = module_cls(**module_args)
        assert isinstance(module, BaseProcessor)
        # TODO: wait here until start() was called for the wrapper module

        module.add_observer(queue_out)
        module.start()
        while active.value:
            module.put(queue_in.get())

        module.stop()

    def _stop(self):
        self._process_active.value = False
        self._queue_in.put(MSPDataFrame(topic=Topic(name="eof"), value=0))
        self._process.join()
