from abc import ABC, abstractmethod
from threading import Thread
from queue import Queue
from multisensor_pipeline.dataframe.dataframe import MSPDataFrame, Topic
from multisensor_pipeline.dataframe import MSPControlMessage
from multisensor_pipeline.modules.base.profiling import MSPModuleStats
from multiprocessing.queues import Queue as MPQueue
from typing import Union, Optional, List
import logging
import uuid

logger = logging.getLogger(__name__)


def add_to_dict(orig_dict, key, value, default=[]):
    if orig_dict.get(key, default) == default:
        orig_dict[key] = [value]
    else:
        orig_dict[key].append(value)


class BaseModule(object):
    """
    Base Class for all Modules
    """

    def __init__(self, profiling=False):
        """
        Initialize the BaseModule
        Args:
           profiling: Option to enable profiling
        """
        self._uuid = uuid.uuid1()
        self._thread = Thread(target=self._worker)
        self._profiling = profiling
        self._stats = MSPModuleStats()
        self._active = False

    def start(self):
        """
        Starts the module.
        """
        logger.debug("starting: {}".format(self.uuid))
        self._active = True
        self.on_start()
        self._thread.start()

    def on_start(self):
        """ Custom initialization """
        pass

    @abstractmethod
    def _worker(self):
        """ Main worker function (async) """
        raise NotImplementedError()

    @abstractmethod
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
        """ Returns if the module is activ """
        return self._active

    @property
    def name(self):
        """ Returns the name of the actual subclass """
        return self.__class__.__name__

    @property
    def uuid(self):
        """ Returns the uuuid of the module """
        return f"{self.name}:{self._uuid.int}"

    @property
    def stats(self) -> MSPModuleStats:
        """ Returns real-time profiling information. """
        return self._stats

    @property
    def profiling(self) -> bool:
        """ Profiling actvice/deactive """
        return self._profiling

    @profiling.setter
    def profiling(self, value):
        self._profiling = value

    def __hash__(self):
        return hash(self.uuid)


class BaseSource(BaseModule, ABC):
    """ Base class for data sources. """

    def __init__(self):
        """
        Initializes the worker thread and a queue list for communication with observers that listen to that source.
        """
        super().__init__()
        self._sinks = {}

    def _worker(self):
        """ Source worker function: notify observer when source update function returns a DataFrame """
        while self._active:
            self._notify(self.on_update())

    @abstractmethod
    def on_update(self) -> Optional[MSPDataFrame]:
        """ Custom update routine. """
        raise NotImplementedError()

    def add_observer(self, sink, topics: Optional[Union[Topic, List[Topic]]] = None):
        """
        Register a Sink or Queue as an observer.

        Args:
            topics:
            sink: A thread-safe Queue object or Sink [or any class that implements put(tuple)]
        """
        if isinstance(sink, Queue) or isinstance(sink, MPQueue):
            if topics is None:
                add_to_dict(self._sinks, None, sink)
            else:
                for topic in topics:
                    add_to_dict(self._sinks, topic, sink)
            return

        assert isinstance(sink, BaseSink) or isinstance(sink, BaseProcessor)
        # if no topic filter is specified
        if topics is None:
            if self.output_topics is None or sink.input_topics is None:
                add_to_dict(self._sinks, None, sink)
                sink.add_source(self)
            else:
                for topic in self.output_topics:
                    if topic in sink.input_topics:
                        add_to_dict(self._sinks, topic, sink)
                        sink.add_source(self)
        else:
            if isinstance(topics, Topic):
                topics = [topics]
            # case: connection with specified topic
            for topic in topics:
                assert self.output_topics is not None, \
                    "you can only specify a topic filter, if output topics are defined"
                # input topics do not need to be defined
                if sink.input_topics is not None:
                    assert topic in self.output_topics and topic in sink.input_topics, \
                        "all topics must be in the output and input topic list"
                    add_to_dict(self._sinks, topic, sink)
                    sink.add_source(self)
                else:
                    "sink does not specify incoming_topics -> therefore it accepts everything TODO: Confirm"
                    add_to_dict(self._sinks, topic, sink)
                    sink.add_source(self)

    def _notify(self, frame: Optional[MSPDataFrame]):
        """
        Notifies all observers that there's a new dataframe

        Args:
            frame: the payload as an instance of MSPDataFrame
        """
        if frame is None:
            return

        # assert isinstance(frame, MSPDataFrame), "You must use a MSPDataFrame instance to wrap your data."
        frame.source_uuid = self.uuid

        # TODO: check if the frame topic is actually an output_topic, send warning if not.

        for topic, sinks in self._sinks.items():
            if topic is None or frame.topic.dtype is MSPControlMessage.ControlTopic.dtype or topic == frame.topic:
                for sink in sinks:
                    sink.put(frame)

        if self._profiling:
            self._stats.add_frame(frame, MSPModuleStats.Direction.OUT)

    def stop(self, blocking: bool = True):
        """
        Stops the source and sends a MSPControlMessage.END_OF_STREAM all observers it stopped

        Args:
            blocking:
        """
        self._notify(MSPControlMessage(message=MSPControlMessage.END_OF_STREAM))
        super(BaseSource, self).stop(blocking=blocking)

    @property
    def output_topics(self) -> Optional[List[Topic]]:
        """ Returns outgoing topics that are provided by the source module at hand. """
        return None


class BaseSink(BaseModule, ABC):
    """ Base class for data sinks. """

    def __init__(self, dropout: Union[bool, float] = False):
        """
        Initializes the worker thread and a queue that will receive new samples from sources.

        Args:
           dropout: Set the max age before elements of the queue are dropped
        """
        super().__init__()
        self._queue = Queue()
        self._active_sources = {}
        self._sources = {}
        self._dropout = dropout  # in seconds
        if dropout and isinstance(dropout, bool):
            self._dropout = 5

    def add_source(self, source: BaseModule):
        """
        Add a source module to be observed

        Args:
           source: Set the max age before elements of the queue are dropped
        """
        self._active_sources[source.uuid] = True

    def _handle_control_message(self, frame: MSPDataFrame):
        """
        Handles incoming control messages from the observed sources (e.g. MSPControlMessage.END_OF_STREAM )

        Args:
           frame: frame containing MSPControlMessage
        """
        if frame.topic.is_control_topic:
            if frame.source_uuid is not None:
                logger.debug(f"[CONTROL] {frame.source_uuid} -> {frame.data} -> {self.uuid}")
            else:
                logger.debug(f"[CONTROL] NONE -> {frame.data} -> {self.uuid}")
            if frame.data == MSPControlMessage.END_OF_STREAM:
                if frame.source_uuid in self._active_sources:
                    # set source to inactive
                    self._active_sources[frame.source_uuid] = False
                    # if no active source is left
                if not any(self._active_sources.values()):
                    self.stop(blocking=False)
            else:
                logger.warning(f"unhandled control message: {frame.data}")
            return True
        return False

    def _worker(self):
        """
        Sink worker function: handles the incoming Dataframes
        """
        while self._active:
            frame = self._queue.get()

            if self._handle_control_message(frame):
                continue

            if self._profiling:
                self._stats.add_frame(frame, MSPModuleStats.Direction.IN)

            self.on_update(frame)

    @abstractmethod
    def on_update(self, frame: MSPDataFrame):
        """ Custom update routine. """
        raise NotImplementedError()

    def _perform_sample_dropout(self, frame_time) -> int:
        # TODO: do this per topic (single queue)
        if not self._dropout:
            return 0

        num_skipped = 0
        with self._queue.mutex:
            while len(self._queue.queue) > 0:
                frame_age = frame_time - self._queue.queue[0].timestamp
                if frame_age > self._dropout:
                    self._queue.queue.popleft()
                    num_skipped += 1
                else:
                    break
        return num_skipped

    def put(self, frame: MSPDataFrame):
        # TODO: create a queue per topic and perform explicit sample synchronization
        skipped_frames = self._perform_sample_dropout(frame.timestamp)
        self._queue.put(frame)
        if self._profiling:
            self._stats.add_queue_state(qsize=self._queue.qsize(), skipped_frames=skipped_frames)

    @property
    def input_topics(self) -> List[Topic]:
        """ Returns topics which can be handled by the sink module at hand. """
        return None


class BaseProcessor(BaseSink, BaseSource, ABC):
    """ Base class for data processors. """

    def _worker(self):
        """
        Processor worker function: handles the incoming dataframe and sends the new processed frame to the observers
        """
        while self._active:
            # get incoming frame
            frame = self._queue.get()
            if self._handle_control_message(frame):
                continue
            if self._profiling:
                self._stats.add_frame(frame, MSPModuleStats.Direction.IN)

            new_frame = self.on_update(frame)

            # send processed frame
            self._notify(new_frame)

    def on_update(self, frame: MSPDataFrame) -> Optional[MSPDataFrame]:
        """ Custom update routine. """
        raise NotImplementedError()
