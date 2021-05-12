from time import sleep
from multisensor_pipeline import GraphPipeline
from multisensor_pipeline.modules.keyboard import Keyboard
from multisensor_pipeline.modules.video.webcam import WebCamSource
from multisensor_pipeline.modules.video.video import VideoSink
from examples.image_processor import ImageProcessor

# create modules
webcam_source = WebCamSource()
image_processor = ImageProcessor()
video_sink = VideoSink(live_preview=False)
keyboard = Keyboard()

# create pipeline
pipeline = GraphPipeline()

# add modules to the pipeline
pipeline.add(modules=[keyboard, image_processor, webcam_source,  video_sink])

# connect modules
pipeline.connect(module=keyboard, successor=image_processor)
pipeline.connect(module=webcam_source, successor=image_processor)
pipeline.connect(module=image_processor,  successor=video_sink)

# start pipeline
pipeline.start()

# let the pipeline run for 10 seconds
sleep(10)

# stop pipeline and join threads
pipeline.stop()
pipeline.join()
