# Multisensor Pipeline (MSP)
The multisensor pipeline (`msp`) package enables stream and event processing with a small amount of dependencies. The main purpose of the `msp` pipeline is the development of research prototypes, but it can also be used for realizing small productive systems or demos that require an acquisition of multiple sensors or data streams (*source*), processing of this data(*processor*), and a utilization of the output (*sink*). The modules in a pipeline form a weakly connected directed graph. Sources and sinks are defined analogously to graph theory, processors are equivalent to internals (see this [Wikipedia article](https://en.wikipedia.org/wiki/Directed_graph#Indegree_and_outdegree)). A pipeline needs at least one source and one sink module. An `msp` pipeline can...

- read/stream signals from any number of **source modules** like sensors, microphones, cameras, pens, eye trackers, etc.
- flexibly process incoming data with **processor modules** (e.g. signal filtering, manipulation, and classification; signal fusion).
- feed data streams to any number of **sink modules** for, e.g., recording data, visualizing data, or as input for user interfaces.

**What are the advantages of `msp`?** 
* It allows to setup flexible processing pipelines with any number of sources, processors and sinks.
* You can easily extend the pipeline by implementing [custom modules](#custom-modules).
* Each module runs in a separate thread to ensure responsiveness.
* Low number of dependecies = easy to integrate in your project.


## Installation
We recommend to use an Anaconda environment with Python 3.6 (x64) or greater. To install the `multisensor_pipeline`, activate your environment of choice and run the following command:

```shell
pip install multisensor-pipeline
```

You can also install the package from source: `python setup.py install`

## Quick Start Example

```python
from multisensor_pipeline import GraphPipeline
from multisensor_pipeline.modules.npy import RandomArraySource, ArrayManipulationProcessor
from multisensor_pipeline.modules import ConsoleSink
from time import sleep
import numpy as np

# define the modules
source = RandomArraySource(shape=(50,), sampling_rate=60)
processor = ArrayManipulationProcessor(numpy_operation=np.mean)
sink = ConsoleSink()

# add module to a pipeline...
pipeline = GraphPipeline()
pipeline.add(modules=[source, processor, sink])
# ...and connect the modules
pipeline.connect(module=source, successor=processor)
pipeline.connect(module=processor, successor=sink)
# (optional) add another edge to print all random numbers
pipeline.connect(module=source, successor=sink)

# print mean of random numbers for 0.1 seconds
pipeline.start()
sleep(.1)
pipeline.stop()
# wait until all processes have stopped
pipeline.join()  
```

The example initializes three modules, one source, one processor and one sink. The `RandomArraySource` generates numpy arrays (ndarray) with random numbers 60 times per second. Each array contains 50 random numbers (shape). The `ArrayManipulationProcessor` takes an array as input, computes the mean of it, and provides it to registered observers. The `ConsoleSink` prints all incoming messages to the console. 

The example contains four major steps:
 
1.  All modules are created and parametrized
2.  The pipeline is created and all modules are added to it.
3.  The modules are connected to build the multisensor pipeline. This step defines what your pipeline is going to do and therefore is the most important step.
    - *source >> processor*: the random arrays are sent to the array manipulator.
    - *processor >> sink*: the manipulated arrays, i.e., the means of them, are sent to the sink module which prints them to the console.
    - *source >> sink*: in addition, all random arrays are printed to the console.
4. Starting and stopping the pipeline: `start()` is starting all modules of the pipeline, e.g., the source starts to generate arrays now. This loop runs infinitely long and has to be stopped from outside by calling the non-blocking `stop()` function of the pipeline instance. You can wait until the pipeline has stopped using its `join()` function.  

## Custom Modules
You can inherit from the `BaseSource`, `BaseProcessor` and `BaseSink` to extend our pipeline. Have a look at the tests and included modules to see how to implement your custom module.

All modules offer or consume data streams frame-by-frame (or both, in case of a processor) using the `MSPDataFrame` class. A source module offers data frames by generating them in `BaseSource.on_update(self) -> MSPDataFrame`. A sink module consumes instances of `MSPDataFrame` in `BaseSource.on_update(self, frame: MSPDataFrame)`. Processors receive an `MSPDataFrame` instance in `on_update(self, frame: MSPDataFrame) -> MSPDataFrame` and return a processed version of it. Each sink or processor module must decide whether and how to process incoming `frame` objects.

### MSPDataFrame

The `MSPDataFrame` class is used to transfer sensor data and meta information from one module to the next. The only required parameter is `topic: Topic` which defines what kind of data the frame delivers. An instance can be created using `BaseModule._generate_topic(self, name: str, dtype: type = None)`. The actual sensor data can be added using key-value pairs (kwargs) when initializing an instance of `MSPDataFrame`. Also, you can add key-value pairs similar to Python `dict`s. The following example shows the `on_update` function of a processor:


```python
# TODO
```
   
Processors and sinks must handle incoming frames and need to decide whether a frame should be processed or not. See the following example code:

```python
def on_update(self, frame: MSPDataFrame) -> MSPDataFrame:
        if frame.topic.name == "mouse.pos":
            self.do_something(frame)
```
 

### Conventions for `data` Parameter
The `data` parameter contains the actual payload of the notification message in terms of an `MSPDataFrame` instance. It enables the transfer of multiple key-value pairs at once with a single timestamp. The values of one dataframe should, semantically and temporally, belong together, e.g., an image and its classification results or a set of IMU measurements like acceleration and orientation coming from a single sensor.
The `MSPDataFrame` class inherits from `dict` can be initialized using a timestamp or without. In the latter case, the current system time is used as timestamp. The data fields can be read and modified as for any Pyhton dictionary. You can also handover an `init_dict` to the constructor to set all fields at once. 
The `MSPEventFrame` inherits from the `MSPDataFrame`. It offers two additional field: *label* and *duration*.

> **Backwards Compatibility:** All modules that do not yet support the new `MSPDataFrame` and demos using these modules were changed in the following way: The `_notify_all` method creates an instance of the `MSPDataFrame` and stores the original payload using the key `"data"`, if any type other than `MSPDataFrame` is given. The `data` variable in all update loops of affected modules is replaced by `data["data"]`. 


Depending on your goals, you can inherit from these base classes to achieve a stronger typing or to add more functionality. Examples for using the base classes are:

* Use `MSPDataFrame` when streaming a sample from a continuous data stream, e.g., a gaze sample, an image frame from a webcam or a random number. You can also use this class for streaming data chunks from, e.g., a microphone. This will enforce that your sample has a timestamp. Any other information can be added as key-value pairs. 
* Use `MSPEventFrame` for pushing events to the pipeline with or without a duration, e.g., a gesture detection or ASR event which have a start time and a duration, or a hotword detection event which has a start time only (and a zero duration). This will enforce that your event has a timestamp, a duration and a label.
* Use a custom implementation, if you want to extend, e.g., which fields shall be enforced. For this, inherit from `MSPDataFrame` or `MSPEventFrame`, add further parameters to the constructor and add access to them via properties. 

### Conventions for Data Types

| Datatype      | Type in MSP           |
|---------------|-----------------------|
| image         | PIL.Image             |
| numeric       | int, float            |
| categorical   | string                |
| array         | list                  |
| complex       | dict                  |

The list and dict data structures can contain any number of types from this table as long as subsequent processors and sinks know how to handle it.

