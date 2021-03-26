from abc import ABC
from threading import Thread
from queue import Queue
from multiprocessing.queues import Queue as MPQueue
from multisensor_pipeline.dataframe.dataframe import MSPDataFrame
from multisensor_pipeline.dataframe.control import MSPControlMessage
import logging

logger = logging.getLogger(__name__)


class BaseModule(object):
    """ Base class for all modules. """

    def __init__(self, profiling=False):
        self._thread = Thread(target=self._worker)
        self._profiling = profiling  # TODO: move to BaseSink? (issue #7)
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
        raise NotImplementedError()

    def _update(self):
        """ Custom update routine. """
        raise NotImplementedError()

    def stop(self, blocking=True):
        """ Stops the module. """
        logger.debug("stopping: {}".format(self.get_name()))
        self._active = False
        if blocking:
            self._thread.join()
        self._stop()

    def _stop(self):
        """ Custom clean-up """
        pass

    def join(self):
        self._thread.join()

    @property
    def active(self):
        return self._active


class BaseSink(BaseModule, ABC):
    """ Base class for data sinks. """

    def __init__(self):
        """ Initializes the worker thread and a queue that will receive new samples from sources. """
        super().__init__()
        self._queue = Queue()
        self._active_sources = {}

    def _add_active_source(self, frame: MSPDataFrame):
        src = frame.topic.source_module
        if src not in self._active_sources:
            self._active_sources[src] = True
            logger.debug(f"new active source: {self.get_name()} <-- {src.__name__}")

    def _handle_control_message(self, frame: MSPDataFrame):
        if isinstance(frame, MSPControlMessage):
            logger.debug(f"[CONTROL] {frame.topic.source_module.__name__} -> {frame.message} -> {self.get_name()}")
            if frame.message == MSPControlMessage.END_OF_STREAM:
                if len(self._active_sources.keys()) == 0:
                    self.stop(blocking=False)
                elif frame.topic.source_module in self._active_sources:
                    # set source to inactive
                    self._active_sources[frame.topic.source_module] = False
                    # if no active source is left
                    if not any(self._active_sources.values()):
                        self.stop(blocking=False)
                        # TODO: check whether this calls the source.stop (for processors)
            else:
                logger.warning(f"unhandled control message: {frame.message}")
            return True
        return False

    def _worker(self):
        while self._active:
            frame = self._queue.get()

            if self._profiling:
                # TODO: update_stats()
                raise NotImplementedError("profiling is not yet implemented, see issue #7")

            if self._handle_control_message(frame):
                continue

            # remember connected source modules
            # TODO: could be replaced by pipeline calls -> hey module, you have the following sources... (#3)
            self._add_active_source(frame)

            self._update(frame)

    def _update(self, frame: MSPDataFrame = None):
        """ Custom update routine. """
        raise NotImplementedError()

    def put(self, sample: MSPDataFrame):
        self._queue.put(sample)

    @property
    def queue_stats(self) -> dict:
        """
        Returns information about the max queue size and the fill state. Also the throughput range, mean.
        Report per source node.
        """
        raise NotImplementedError()


class BaseSource(BaseModule, ABC):
    """ Base class for data sources. """

    def __init__(self):
        """
        Initializes the worker thread and a queue list for communication with observers that listen to that source.
        """
        super().__init__()
        self._sinks = []

    def _worker(self):
        while self._active:
            self._notify(self._update())

    def _update(self) -> MSPDataFrame:
        """ Custom update routine. """
        raise NotImplementedError()

    def add_observer(self, sink):
        """
        Register a Sink or Queue as an observer.

        Args:
            sink: A thread-safe Queue object or Sink [or any class that implements put(tuple)]
        """
        if isinstance(sink, Queue) or isinstance(sink, MPQueue):
            self._sinks.append(sink)
            return

        assert isinstance(sink, BaseSink) or isinstance(sink, BaseProcessor)
        self._sinks.append(sink)
        # TODO: check if types match -> raise error or warning

    def _notify(self, frame: MSPDataFrame):
        """
        Notifies all observers that there's a new dataframe

        Args:
            frame: the payload as an instance of MSPDataFrame
        """
        assert isinstance(frame, MSPDataFrame), "You must use a MSPDataFrame instance to wrap your data."

        for sink in self._sinks:
            sink.put(frame)
            
    def stop(self, blocking=True):
        # send end-of-stream message
        self._notify(MSPControlMessage(message=MSPControlMessage.END_OF_STREAM, source_module=self.__class__))
        super(BaseSource, self).stop(blocking=blocking)


class BaseProcessor(BaseSink, BaseSource, ABC):
    """ Base class for data processors. """
