from abc import ABC
from threading import Thread
from queue import Queue
from ..utils.dataframe import MSPDataFrame, TypeInfo, TypeMismatchException
import logging
import warnings

logger = logging.getLogger(__name__)


class BaseModule(object):
    """ Base class for all modules. """

    def __init__(self):
        self._thread = Thread(target=self._worker)
        self._active = False

    def get_name(self):
        """ Returns the name of the actual subclass """
        return self.__class__.__name__

    def start(self):
        """ Starts the module. """
        logger.debug("starting: {}".format(self.get_name()))
        self._active = True
        self._start()
        self._thread.start()

    def _start(self):
        """ Custom initialization """
        pass

    def _worker(self):
        """ Main worker function (async) """
        self._update()

    def _update(self, frame: MSPDataFrame = None):
        """ Custom update routine. """
        raise NotImplementedError()

    def stop(self):
        """ Stops the module. """
        logger.debug("stopping: {}".format(self.get_name()))
        self._active = False
        self._thread.join()
        self._stop()

    def _stop(self):
        """ Custom clean-up """
        pass


class BaseSink(BaseModule, ABC):
    """ Base class for data sinks. """

    def __init__(self):
        """ Initializes the worker thread and a queue that will receive new samples from sources. """
        super().__init__()
        self._source_queue = Queue()
        self._consumes = None

    def _worker(self):
        while self._active:
            frame = self.get()
            self._update(frame)

    def put(self, sample):
        self._source_queue.put(sample)

    def get(self):
        return self._source_queue.get()

    @property
    def consumes(self):
        return self._consumes


class BaseSource(BaseModule, ABC):
    """ Base class for data sources. """

    def __init__(self):
        """
        Initializes the worker thread and a queue list for communication with observers that listen to that source.
        """
        super().__init__()
        self._sinks = []
        self._offers = None

    def add_observer(self, sink):
        """
        Register a Sink or Queue as an observer.

        Args:
            sink: A thread-safe Queue object or Sink [or any class that implements put(tuple)]
        """
        if isinstance(sink, Queue):
            self._sinks.append(sink)
            return

        assert isinstance(sink, BaseSink) or isinstance(sink, BaseProcessor)
        if TypeInfo.multi_match(self, sink):
            self._sinks.append(sink)
            return

        raise TypeMismatchException(self, sink)

    def _notify_all(self, frame: MSPDataFrame):
        """
        Notifies all observers that there's a new dataframe

        Args:
            frame: the payload as an instance of MSPDataFrame
        """
        # TODO: enforce using MSPDataFrame instances
        if not isinstance(frame, MSPDataFrame):
            warnings.warn("use MSPDataFrames, unwrapped payloads won't be accepted in v2.0.0", DeprecationWarning)
            frame = MSPDataFrame(init_dict={"data": frame})

        for sink in self._sinks:
            sink.put(frame)

    @property
    def offers(self):
        return self._offers


class BaseProcessor(BaseSink, BaseSource, ABC):
    """ Base class for data processors. """

    def _dtype_out(self, dtype_in, suffix):
        if suffix is None:
            return dtype_in
        base_dtype = dtype_in if isinstance(dtype_in, str) else dtype_in.decode()
        dtype_out = f"{base_dtype}.{suffix}"
        return dtype_out if isinstance(dtype_in, str) else dtype_out.encode()

    def _notify_all(self, frame, suffix=None):
        frame.dtype = self._dtype_out(frame.dtype, suffix)
        super(BaseProcessor, self)._notify_all(frame)
