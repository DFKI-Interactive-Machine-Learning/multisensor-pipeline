from multisensor_pipeline.dataframe import MSPDataFrame, Topic


class MSPControlMessage(MSPDataFrame):

    END_OF_STREAM = "EOS"

    def __init__(self, message, source):
        topic = Topic(name="control", source_module=source.name, source_uuid=source.uuid)
        super(MSPControlMessage, self).__init__(topic=topic, value=message)

    @property
    def message(self):
        return self.value
