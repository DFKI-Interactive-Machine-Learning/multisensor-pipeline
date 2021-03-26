from .base import PipelineBase
from multisensor_pipeline.modules.base import *
import networkx as nx

from ..dataframe import MSPDataFrame


class GraphPipeline(PipelineBase):

    ROLE_SOURCE = "source"
    ROLE_PROCESSOR = "processor"
    ROLE_SINK = "sink"

    def __init__(self):
        self._graph = nx.DiGraph()

    def add_source(self, source_node: BaseSource):
        assert isinstance(source_node, BaseSource)
        self._graph.add_node(source_node, role=self.ROLE_SOURCE)

    def add_processor(self, processor_node: BaseProcessor):
        assert isinstance(processor_node, BaseProcessor)
        self._graph.add_node(processor_node, role=self.ROLE_PROCESSOR)

    def add_sink(self, sink_node: BaseSink):
        assert isinstance(sink_node, BaseSink)
        self._graph.add_node(sink_node, role=self.ROLE_SINK)

    def connect(self, node, successor):
        node.add_observer(successor)  # must be first, because it implicitly validates the connection
        successor.add_source(node)
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
    def active_modules(self):
        """ Number of active modules. Not counting queues. """
        return [n for n in self.nodes if n.active]

    @property
    def size(self):
        """ Returns the number of connections in the pipeline (edges in the underlying graph). """
        return self._graph.size()

    def check_pipeline(self):
        """ The multisensor-pipeline must be a weakly connected directed graph. """
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
        return any([not n.active for n in self._graph.successors(node)])

    def _start_reversed(self, node):
        """ Starts nodes in a depth first search. """
        if isinstance(node, BaseModule):
            # start module (queues don't need to be started)
            node.start()
        for n in self._graph.predecessors(node):
            if self._has_inactive_successors(n):
                continue  # will be started when coming from another sink node
            if n.active:
                continue
            self._start_reversed(n)

    def start(self):
        """ Start the pipeline. """
        self.check_pipeline()
        for node in self.sink_nodes:
            self._start_reversed(node)

    def stop(self):
        """ Stop the pipeline. """
        for node in self.source_nodes:
            node.stop(blocking=False)

    def join(self):
        for node in self.sink_nodes:
            node.join()


class SubGraphPipeline(GraphPipeline, BaseProcessor):
    """ A pipeline that can be used like a BaseProcessor """

    def __init__(self):
        super().__init__()
        raise NotImplementedError()

    def _update(self, frame: MSPDataFrame = None):
        raise NotImplementedError()

    @property
    def queue_stats(self) -> dict:
        raise NotImplementedError()

    def check_pipeline(self):
        raise NotImplementedError()
