from multisensor_pipeline.modules.base import BaseSource, BaseSink, BaseProcessor, BaseModule
from abc import ABC, abstractmethod
import networkx as nx
import logging

logger = logging.getLogger(__name__)


class PipelineBase(ABC):

    # TODO: add option: profiling -> use for modules init. (#7)
    #  + Add property for dashboard access (pipeline is model for dashboard view)

    @abstractmethod
    def check_pipeline(self):
        raise NotImplementedError()

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass


class GraphPipeline(PipelineBase):

    ROLE_SOURCE = "source"
    ROLE_PROCESSOR = "processor"
    ROLE_SINK = "sink"

    def __init__(self):
        self._graph = nx.DiGraph()

    def add_source(self, source_node: BaseSource):
        self._graph.add_node(source_node, role=self.ROLE_SOURCE, active=False)

    def add_processor(self, processor_node: BaseProcessor):
        self._graph.add_node(processor_node, role=self.ROLE_PROCESSOR, active=False)

    def add_sink(self, processor_node: BaseSink):
        self._graph.add_node(processor_node, role=self.ROLE_SINK, active=False)

    def connect(self, node, successor):
        node.add_observer(successor)  # must be first, because it implicitly validates the connection
        self._graph.add_edge(node, successor)

    def get_nodes_with_attribute(self, attribute, value):
        return [node[0] for node in self._graph.nodes(data=attribute) if node[1] == value]

    @property
    def source_nodes(self):
        return self.get_nodes_with_attribute("role", self.ROLE_SOURCE)

    @property
    def processor_nodes(self):
        return self.get_nodes_with_attribute("role", self.ROLE_PROCESSOR)

    @property
    def sink_nodes(self):
        return self.get_nodes_with_attribute("role", self.ROLE_SINK)

    @property
    def nodes(self):
        return self._graph.nodes()

    @property
    def size(self):
        """Returns the number of connections in the pipeline (edges in the underlying graph)."""
        return self._graph.size()

    def check_pipeline(self):
        """The multisensor-pipeline is a directed graph and valid, if it is weakly connected."""
        sources = self.source_nodes
        assert len(sources) > 0, "a valid pipeline requires at least a source"
        for node in sources:
            assert len(list(self._graph.successors(node))) > 0, node
            assert len(list(self._graph.predecessors(node))) == 0, node

        for node in self.processor_nodes:  # this is a redundant check (never happens, if graph is weakly connected)
            assert len(list(self._graph.successors(node))) > 0, node
            assert len(list(self._graph.predecessors(node))) > 0, node

        sinks = self.sink_nodes
        assert len(sinks) > 0, "a valid pipeline requires at least a sink"
        for node in self.sink_nodes:
            assert len(list(self._graph.successors(node))) == 0, node
            assert len(list(self._graph.predecessors(node))) > 0, node

        # no unconnected nodes or subgraphs are allowed
        assert nx.is_weakly_connected(self._graph), "all nodes in the pipeline have to be connected, they are not"

        return True

    def _has_inactive_successors(self, node):
        successor_active_states = [not self._graph.nodes[n]["active"] for n in self._graph.successors(node)]
        return any(successor_active_states)

    def _start_reversed(self, node):
        """Starts nodes in a depth first search and stops, if all predecessors have at least one inactive successor."""
        if isinstance(node, BaseModule):
            node.start()  # this ignores queues which don't need to be started
        self._graph.nodes[node]["active"] = True  # TODO: remove if node.is_active works as well
        for n in self._graph.predecessors(node):
            if self._has_inactive_successors(n):
                continue  # will be started when coming from another sink node
            if self._graph.nodes[n]["active"]:
                continue
            self._start_reversed(n)

    def start(self):
        """Start all nodes in the pipeline in reverse order."""
        self.check_pipeline()
        for node in self.sink_nodes:
            self._start_reversed(node)

    def _has_active_successors(self, node):
        successor_active_states = [self._graph.nodes[n]["active"] for n in self._graph.successors(node)]
        return any(successor_active_states)

    def _stop_reversed(self, node):
        """Starts nodes in a depth first search and stops, if all predecessors have at least one inactive successor."""
        if isinstance(node, BaseModule):
            node.stop()  # this ignores queues which don't need to be started
        self._graph.nodes[node]["active"] = False  # TODO: remove if node.is_active works as well
        for n in self._graph.predecessors(node):
            if self._has_active_successors(n):
                continue  # will be started when coming from another sink node
            if not self._graph.nodes[n]["active"]:
                continue
            self._stop_reversed(n)

    def stop(self):
        """iterate through the graph and stop, see gocl example"""
        for node in self.sink_nodes:
            self._stop_reversed(node)


class LinearPipeline(PipelineBase):

    def __init__(self, pipeline=None):
        if pipeline is None:
            self._pipeline = []
        else:
            self._pipeline = pipeline

    def append(self, p):
        """Can be used to assemble a simple linear pipeline."""
        if len(self._pipeline) == 0:
            assert isinstance(p, BaseSource)
        if len(self._pipeline) > 0:
            assert not isinstance(p, BaseSource)
        self._pipeline.append(p)

    @property
    def pipeline(self):
        return self._pipeline

    @property
    def is_valid(self):
        res, err = self.check_pipeline(self._pipeline)
        return res

    @property
    def source(self) -> BaseSource:
        if self.is_valid:
            return self._pipeline[0]
        else:
            return None

    @property
    def sink(self) -> BaseSink:
        if self.is_valid:
            return self._pipeline[-1]
        else:
            return None

    def check_pipeline(self):
        pipeline = self.pipeline
        if not isinstance(pipeline, list):
            return False, "pipeline must be of type list."
        if len(pipeline) < 2:
            return False, "pipeline needs at least one source and one sink."
        if not isinstance(pipeline[0], BaseSource) or not isinstance(pipeline[-1], BaseSink):
            return False, "pipeline requires a source at index 0 and a sink at its end."
        if len(pipeline) > 2:
            for p in pipeline[1:-1]:
                # TODO: if not isinstance(p, base_processor) -> in between only processors are allowed
                pass

        return True, None

    def start(self):
        is_valid, err = self.check_pipeline(self._pipeline)

        if is_valid:
            for p, p_next in zip(reversed(self._pipeline[:-1]), reversed(self._pipeline[1:])):
                p.add_observer(p_next)
                p_next.start()
            self.source.start()

        else:
            err_msg = "you tried to start an invalid pipeline: {}".format(err)
            logger.error(err_msg)
            raise AssertionError(err_msg)

    def stop(self):
        for p in reversed(self._pipeline):
            p.stop()
