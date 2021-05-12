from abc import ABC, abstractmethod


class PipelineBase(ABC):

    # TODO: add option: profiling -> use for modules init. (#7)
    # + Add property for dashboard access
    # (pipeline is model for dashboard view)

    @abstractmethod
    def check_pipeline(self):
        raise NotImplementedError()

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass
