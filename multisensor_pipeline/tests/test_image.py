import unittest
from typing import Optional, List
from PIL import Image
from time import sleep

from multisensor_pipeline.dataframe.dataframe import MSPDataFrame, Topic
from multisensor_pipeline.modules.base.base import BaseSource
from multisensor_pipeline.modules.image.pillow import CropByPointerProcessor
from multisensor_pipeline.modules.npy import RandomArraySource
from multisensor_pipeline.modules import TrashSink, ListSink
from multisensor_pipeline.pipeline.graph import GraphPipeline


class EmptyImageSource(BaseSource):

    def on_update(self) -> Optional[MSPDataFrame]:
        image = Image.new(mode="RGBA", size=(1000, 1000), color=(0, 0, 0, 254))
        return MSPDataFrame(self.output_topics[0], data=image)

    @property
    def output_topics(self) -> Optional[List[Topic]]:
        return [Topic(name="empty_image", dtype=Image.Image)]


class ImageCroppingTest(unittest.TestCase):
    def test_simple_cropping(self):
        img_source = EmptyImageSource()
        pnt_source = RandomArraySource(
            shape=(2,), min=0, max=255, sampling_rate=5, max_count=5
        )
        crop_processor = CropByPointerProcessor(
            crop_size=200,
            pointer_topic_name="random"
        )

        sink = ListSink()

        pipeline = GraphPipeline()
        pipeline.add([img_source, pnt_source, crop_processor, sink])
        pipeline.connect(img_source, crop_processor)
        pipeline.connect(pnt_source, crop_processor)
        pipeline.connect(crop_processor, sink)
        pipeline.start()
        sleep(1)
        pipeline.stop()
        pipeline.join()

        # TODO: Check if 5 should be enforced (if a pointer is sent before image is loaded, should the processor wait?)
        self.assertEqual(len(sink), 5)
