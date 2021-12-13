from abc import ABC, abstractmethod
from multisensor_pipeline.dataframe import MSPDataFrame, MSPControlMessage
from multisensor_pipeline.modules.base import BaseSink, BaseSource, BaseModule, BaseProcessor
from typing import Optional
import multiprocessing as mp
import logging

logger = logging.getLogger(__name__)


def initialize_module_and_wait_for_start(module_cls, module_args, init_event, start_event) -> BaseModule:
    module = module_cls(**module_args)
    assert isinstance(module, BaseModule)
    # allow others to wait until the initialization is done
    init_event.set()
    # wait until start() was called
    start_event.wait()
    return module


class MultiprocessModuleWrapper(BaseModule, ABC):

    def __init__(self, module_cls: type, **module_args):
        super(MultiprocessModuleWrapper, self).__init__()

        self._wrapped_module_cls = module_cls
        self._wrapped_module_args = module_args

        self._init_event = mp.Event()
        self._start_event = mp.Event()
        self._stop_event = mp.Event()
        self._process = self._init_process()
        self._process.start()

    @abstractmethod
    def _init_process(self) -> mp.Process:
        raise NotImplementedError()

    @abstractmethod
    def _stop_process(self):
        raise NotImplementedError()

    def on_start(self):
        self._init_event.wait()  # Wait until initialization is finished
        self._start_event.set()  # Start the main loop of the process

    @staticmethod
    @abstractmethod
    def _process_worker(module_cls: type, module_args: dict, init_event, start_event, stop_event, queue):
        raise NotImplementedError()


class MultiprocessSourceWrapper(MultiprocessModuleWrapper, BaseSource):

    def _init_process(self) -> mp.Process:
        self._queue_out = mp.Queue()
        return mp.Process(target=self._process_worker,
                          args=(self._wrapped_module_cls, self._wrapped_module_args, self._init_event,
                                self._start_event, self._stop_event, self._queue_out))

    @staticmethod
    def _process_worker(module_cls: type, module_args: dict, init_event, start_event, stop_event, queue_out):
        module = initialize_module_and_wait_for_start(module_cls, module_args, init_event, start_event)
        assert isinstance(module, BaseSource)

        module.add_observer(queue_out)
        module.start()
        stop_event.wait()
        module.stop()

    def on_update(self) -> Optional[MSPDataFrame]:
        return self._queue_out.get()

    def _stop_process(self):
        logger.debug("stopping: {}.{}".format(self.name, self._wrapped_module_cls.__name__))
        # ask module process to stop
        self._stop_event.set()
        self._process.join()

    def stop(self, blocking=False):
        """ Stops the module. """
        self._stop_process()
        super(MultiprocessModuleWrapper, self).stop(blocking=blocking)
        eof_msg = MSPControlMessage(message=MSPControlMessage.END_OF_STREAM)
        self._queue_out.put(eof_msg)


class MultiprocessSinkWrapper(MultiprocessModuleWrapper, BaseSink):

    def _init_process(self) -> mp.Process:
        self._queue_in = mp.Queue()
        return mp.Process(target=self._process_worker,
                          args=(self._wrapped_module_cls, self._wrapped_module_args, self._init_event,
                                self._start_event, self._stop_event, self._queue_in))

    @staticmethod
    def _process_worker(module_cls: type, module_args: dict, init_event, start_event, stop_event, queue_in):
        module = initialize_module_and_wait_for_start(module_cls, module_args, init_event, start_event)
        assert isinstance(module, BaseSink)

        module.start()
        while not stop_event.is_set() or not queue_in.empty():
            module.put(queue_in.get())

    def on_update(self, frame: MSPDataFrame):
        self._queue_in.put(frame)

    def _stop_process(self):
        logger.debug("stopping: {}.{}".format(self.name, self._wrapped_module_cls.__name__))
        # ask module process to stop
        self._stop_event.set()
        eof_msg = MSPControlMessage(message=MSPControlMessage.END_OF_STREAM)
        self._queue_in.put(eof_msg)
        self._process.join()

    def stop(self, blocking=False):
        """ Stops the module. """
        self._stop_process()
        super(MultiprocessModuleWrapper, self).stop(blocking=blocking)


class MultiprocessProcessorWrapper(MultiprocessSinkWrapper, MultiprocessSourceWrapper, BaseProcessor):

    def _init_process(self) -> mp.Process:
        self._queue_in = mp.Queue()
        self._queue_out = mp.Queue()
        return mp.Process(target=self._process_worker,
                          args=(self._wrapped_module_cls, self._wrapped_module_args, self._init_event,
                                self._start_event, self._stop_event, self._queue_in, self._queue_out))

    def on_update(self, frame: MSPDataFrame) -> Optional[MSPDataFrame]:
        self._queue_in.put(frame)
        return self._queue_out.get()

    @staticmethod
    def _process_worker(module_cls: type, module_args: dict, init_event, start_event, stop_event, queue_in, queue_out):
        module = initialize_module_and_wait_for_start(module_cls, module_args, init_event, start_event)
        assert isinstance(module, BaseProcessor)

        module.add_observer(queue_out)
        module.start()
        while not stop_event.is_set():
            module.put(queue_in.get())
