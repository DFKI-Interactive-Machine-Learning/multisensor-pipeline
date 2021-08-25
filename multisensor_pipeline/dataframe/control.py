from multisensor_pipeline.dataframe import MSPDataFrame, Topic


class MSPControlMessage(MSPDataFrame):

    class ControlTopic(Topic):
        class ControlType:
            pass
        name = None
        dtype = ControlType

    END_OF_STREAM = "EOS"

    def __init__(self, message):
        topic = self.ControlTopic()
        super(MSPControlMessage, self).__init__(topic=topic, message=message)

    @property
    def message(self):
        return self['message']
