from abc import ABC
from threading import Thread
from queue import Queue
from multiprocessing.queues import Queue as MPQueue
from multisensor_pipeline.dataframe.dataframe import MSPDataFrame, Topic
from multisensor_pipeline.dataframe.control import MSPControlMessage
from typing import Union, Optional
import logging
import uuid

logger = logging.getLogger(__name__)


class BaseModule(object):
    """ Base class for all modules. """

    def __init__(self, profiling=False):
        self._uuid = uuid.uuid1()
        self._thread = Thread(target=self._worker)
        self._profiling = profiling
        self._active = False

    def start(self):
        """ Starts the module. """
        logger.debug("starting: {}".format(self.uuid))
        self._active = True
        self.on_start()
        self._thread.start()

    def _generate_topic(self, name: str, dtype: type = None):
        return Topic(name=name, dtype=dtype, source_module=self.__class__, source_uuid=self.uuid)

    def on_start(self):
        """ Custom initialization """
        pass

    def _worker(self):
        """ Main worker function (async) """
        raise NotImplementedError()

    def on_update(self):
        """ Custom update routine. """
        raise NotImplementedError()

    def stop(self, blocking=True):
        """ Stops the module. """
        logger.debug("stopping: {}".format(self.uuid))
        self._active = False
        if blocking:
            self._thread.join()
        self.on_stop()

    def on_stop(self):
        """ Custom clean-up """
        pass

    def join(self):
        self._thread.join()

    @property
    def active(self):
        return self._active

    @property
    def name(self):
        """ Returns the name of the actual subclass """
        return self.__class__.__name__

    @property
    def uuid(self):
        return f"{self.name}:{self._uuid.int}"

    @property
    def stats(self) -> dict:
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
            frame = self.on_update()

            if self._profiling:
                # TODO: update_stats()
                raise NotImplementedError("profiling is not yet implemented, see issue #7")

            self._notify(frame)

    def on_update(self) -> Optional[MSPDataFrame]:
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
        sink.add_source(self)
        self._sinks.append(sink)
        # TODO: check if types match -> raise error or warning

    def _notify(self, frame: Optional[MSPDataFrame]):
        """
        Notifies all observers that there's a new dataframe

        Args:
            frame: the payload as an instance of MSPDataFrame
        """
        if frame is None:
            return

        assert isinstance(frame, MSPDataFrame), "You must use a MSPDataFrame instance to wrap your data."

        for sink in self._sinks:
            sink.put(frame)

    def stop(self, blocking=True):
        # send end-of-stream message
        self._notify(MSPControlMessage(message=MSPControlMessage.END_OF_STREAM, source=self))
        super(BaseSource, self).stop(blocking=blocking)


class BaseSink(BaseModule, ABC):
    """ Base class for data sinks. """

    def __init__(self, dropout: Union[bool, float] = False):
        """ Initializes the worker thread and a queue that will receive new samples from sources. """
        super().__init__()
        self._queue = Queue()
        self._active_sources = {}
        self._dropout = dropout  # in seconds
        if dropout and isinstance(dropout, bool):
            self._dropout = 5

    def add_source(self, source: BaseModule):
        self._active_sources[source.uuid] = True

    def _handle_control_message(self, frame: MSPDataFrame):
        if isinstance(frame, MSPControlMessage):
            logger.debug(f"[CONTROL] {frame.topic.source_uuid} -> {frame.message} -> {self.uuid}")
            if frame.message == MSPControlMessage.END_OF_STREAM:
                if frame.topic.source_uuid in self._active_sources:
                    # set source to inactive
                    self._active_sources[frame.topic.source_uuid] = False
                    # if no active source is left
                if not any(self._active_sources.values()):
                    self.stop(blocking=False)
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

            self.on_update(frame)

    def on_update(self, frame: MSPDataFrame):
        """ Custom update routine. """
        raise NotImplementedError()

    def _perform_sample_dropout(self, frame_time):
        if not self._dropout:
            return

        with self._queue.mutex:
            while len(self._queue.queue) > 0:
                frame_age = frame_time - self._queue.queue[0].timestamp
                if frame_age > self._dropout:
                    self._queue.queue.popleft()
                else:
                    break

    def put(self, frame: MSPDataFrame):
        self._perform_sample_dropout(frame.timestamp)
        self._queue.put(frame)


class BaseProcessor(BaseSink, BaseSource, ABC):
    """ Base class for data processors. """

    def _worker(self):
        while self._active:
            # get incoming frame
            frame = self._queue.get()
            if self._profiling:
                # TODO: update_stats() (sink)
                raise NotImplementedError("profiling is not yet implemented, see issue #7")
            if self._handle_control_message(frame):
                continue

            new_frame = self.on_update(frame)

            # send processed frame
            if self._profiling:
                # TODO: update_stats() (source)
                raise NotImplementedError("profiling is not yet implemented, see issue #7")
            self._notify(new_frame)

    def on_update(self, frame: MSPDataFrame) -> Optional[MSPDataFrame]:
        """ Custom update routine. """
        raise NotImplementedError()
