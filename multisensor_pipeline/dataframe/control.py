from multisensor_pipeline.dataframe import MSPDataFrame, Topic


class MSPControlMessage(MSPDataFrame):

    EMPTY = "EMTPY"
    END_OF_STREAM = "EOS"
    END_OF_FILE = "EOF"

    def __init__(self, message, source):
        topic = Topic(name="control", source_module=source.name, source_uuid=source.uuid)
        super(MSPControlMessage, self).__init__(topic=topic, message=message)

    @property
    def message(self):
        return self['message']
