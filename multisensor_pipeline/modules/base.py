from abc import ABC
from multisensor_pipeline.utils.dataframe import TypeInfo, TypeMismatchException
from threading import Thread
from queue import Queue
from ..utils.dataframe import MSPDataFrame
import logging

logger = logging.getLogger(__name__)


class BaseModule(object):
    """
    Base class for all modules.
    """

    def __init__(self):
        self._thread = Thread(target=self._update_loop)
        self._active = False

    def get_name(self):
        """
        Returns: Name of the actual subclass
        """
        return self.__class__.__name__

    def start(self):
        """
        Starts the module.
        """
        logger.debug("starting: {}".format(self.get_name()))
        self._active = True
        self._start()
        self._thread.start()

    def _start(self):
        """
        Custom initialization
        """
        pass

    def _update_loop(self):
        """
        Main worker function (async)
        """
        raise NotImplementedError()

    def stop(self):
        """
        Stops the module.
        """
        logger.debug("stopping: {}".format(self.get_name()))
        self._active = False
        self._thread.join()
        self._stop()

    def _stop(self):
        """
        Custom clean-up
        """
        pass


class BaseSink(BaseModule, ABC):
    """
    Base class for data sinks.
    """

    def __init__(self):
        """
        Initializes the worker thread and a queue that will receive new samples from sources.
        """
        super().__init__()
        self._source_queue = Queue()
        self._consumes = None  # TODO: maybe set to None: the implementation should know what it consumes.

    def put(self, sample):
        self._source_queue.put(sample)

    def get(self):
        return self._source_queue.get()

    @property
    def consumes(self):
        return self._consumes


class BaseSource(BaseModule, ABC):
    """
    Base class for data sources.
    """

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

    def _notify_all(self, dtype, data: MSPDataFrame):
        """
        Notifies all observers that there's new data

        Args:
            dtype: string describing the data event
            data: the actual payload as an instance of MSPDataFrame
        """
        # TODO: switch to TypeInfo, create TypeInfo with str, if it's not a TypeInfo instance

        if type(dtype) is not bytes:
            dtype = str(dtype).encode()

        if not isinstance(data, MSPDataFrame):
            # TODO: update all tests and demos accordingly (it should be sufficient to insert payload=payload["data"])
            data = MSPDataFrame(init_dict={"data": data})

        for sink in self._sinks:
            sink.put((dtype, data))

    @property
    def offers(self):
        return self._offers


class BaseProcessor(BaseModule, ABC):
    """
    Base class for data sinks.
    """

    def __init__(self):
        """
        Initializes the worker thread and a queue that will receive new samples from sources.
        """
        super().__init__()
        self._sink = BaseSink()
        self._source = BaseSource()

    def put(self, sample):
        self._sink.put(sample)

    def get(self):
        return self._sink.get()

    @property
    def consumes(self):
        return self._sink.consumes

    @property
    def offers(self):
        return self._source.offers

    def add_observer(self, sink):
        self._source.add_observer(sink)

    def _dtype_out(self, dtype_in, suffix):
        if suffix is None:
            return dtype_in
        base_dtype = dtype_in if isinstance(dtype_in, str) else dtype_in.decode()
        dtype_out = f"{base_dtype}.{suffix}"
        return dtype_out if isinstance(dtype_in, str) else dtype_out.encode()

    def _notify_all(self, dtype, data, suffix=None):
        self._source._notify_all(self._dtype_out(dtype, suffix), data)
