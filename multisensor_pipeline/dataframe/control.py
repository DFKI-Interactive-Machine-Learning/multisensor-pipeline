from multisensor_pipeline.dataframe.dataframe import MSPDataFrame, Topic


class MSPControlMessage(MSPDataFrame):

    END_OF_STREAM = "EOS"

    def __init__(self, message, source):
        """Create an instance of a msp control message."""
        topic = Topic(
            name="control",
            source_module=source.name,
            source_uuid=source.uuid,
        )
        super(MSPControlMessage, self).__init__(
            topic=topic,
            message=message,
        )

    @property
    def message(self):
        return self['message']
