from typing import Optional
from PIL import Image
from time import sleep

from multisensor_pipeline.dataframe.dataframe import MSPDataFrame
from multisensor_pipeline.modules.base.base import BaseSource
from multisensor_pipeline.modules.image.pillow import CropByPointerProcessor
from multisensor_pipeline.modules.npy import RandomArraySource
from multisensor_pipeline.modules import TrashSink
from multisensor_pipeline.pipeline.graph import GraphPipeline


class EmptyImageSource(BaseSource):

    def on_update(self) -> Optional[MSPDataFrame]:
        image = Image.new(mode="RGBA", size=(1000, 1000), color=(0, 0, 0, 254))
        return MSPDataFrame(
            self._generate_topic(name="empty_image", dtype=Image.Image),
            image=image
        )


class ImageCroppingTest(unittest.TestCase):
    def test_simple_cropping(self):
        img_source = EmptyImageSource()
        pnt_source = RandomArraySource(
            shape=(2,), min=0, max=255, sampling_rate=5
        )
        crop_processor = CropByPointerProcessor(
            image_topic_name="empty_image",
            image_key="image",
            pointer_topic_names=["random"],
            point_key="value",
        )
        sink = TrashSink()

        p = GraphPipeline()
        p.add([img_source, pnt_source, crop_processor, sink])
        p.connect(img_source, crop_processor)
        p.connect(pnt_source, crop_processor)
        p.connect(crop_processor, sink)
        p.start()
        sleep(1)
        p.stop()
        p.join()

        self.assertEqual(True, True)
