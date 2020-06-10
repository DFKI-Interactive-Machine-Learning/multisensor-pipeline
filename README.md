# Multisensor Pipeline (MSP)
This repository contains the implementation of a multisensor pipeline which can be used for different purposes:

- reading/streaming of signals from **source modules** like sensors, microphones, cameras, pens, eye trackers etc.
- flexibly processing incoming data with **processor modules** (e.g. speech recognition, object detection, fixation detection)
- feed data streams to any number of **sink modules** for, e.g., recording data, visualizing data or using inputs/events for interaction.

This framework allows to setup flexible processing pipelines with any number of sources, processors and sinks. The connected modules form a weakly connected directed graph. Sources and sinks are defined analogously to graph theory, processors are equivalent to internals (see this [Wikipedia article](https://en.wikipedia.org/wiki/Directed_graph#Indegree_and_outdegree)). Requirements are that a pipeline needs at least one source and one sink, and connected modules must have at least one matching data type.

## Install
We recommend to use an Anaconda environment with Python 3.7 (x64). To install the `multisensor_pipeline`, activate your environment of choice and run one of the following commands:

* for using PyPi run `python -m pip install multisensor-pipeline`
* for using a pre-built wheel run `python -m pip install multisensor_pipeline-<version>-<meta-info>.whl`
* for installing from source run `python setup.py install`

## Example

```python
from multisensor_pipeline.pipeline import GraphPipeline
from multisensor_pipeline.modules.numpy import RandomArraySource, ArrayManipulationProcessor
from multisensor_pipeline.modules.console import ConsoleSink
from time import sleep
import numpy as np

# (1) define the modules
source = RandomArraySource(shape=(50,), frequency=60)
processor = ArrayManipulationProcessor(np.mean)
sink = ConsoleSink()

# (2) add module to a pipeline...
pipeline = GraphPipeline()
pipeline.add_source(source)
pipeline.add_processor(processor)
pipeline.add_sink(sink)
# (3) ...and connect the modules
pipeline.connect(source, processor)
pipeline.connect(processor, sink)
# (optional) add another edge to print all random numbers
pipeline.connect(source, sink)

# (4) print mean of random numbers for 0.1 seconds
pipeline.start()
sleep(.1)
pipeline.stop()

```

The example initializes three modules, one source, one processor and one sink. The `RandomArraySource` generates numpy arrays (ndarray) with random numbers 60 times per second. Each array contains 50 random numbers (shape). The `ArrayManipulationProcessor` takes an array as input, computes the mean of it, and provides it to registered observers. The `ConsoleSink` prints all incoming messages to the console. 

The example contains four major steps:
 
1.  All modules are created and parametrized
2.  The pipeline is created and all modules are added to it with their specific role (source, processor or sink)
3.  The modules are connected to build the multisensor pipeline. This step defines what your pipeline is going to do and therefore is the most important step.
    - *source >> processor*: the random arrays are sent to the array manipulator.
    - *processor >> sink*: the manipulated arrays, i.e., the means of them, are sent to the sink module which prints them to the console.
    - *source >> sink*: You can add multiple edges. This edge causes that the arrays are printed as well.
4. Starting and stopping the pipeline: `start()` is starting all individual modules, e.g., now the source starts to generate the arrays and so on. This loop runs infinitely long and has to be stopped from outside by calling the `stop()` function of the pipeline instance.

## Custom Modules
You can inherit from the `BaseSource`, `BaseProcessor` and `BaseSink` to extend our pipeline. Have a look at the tests and core modules to see how to implement your custom module.

## Data Format Conventions

All modules offer or consume data streams (or both, in case of a processor). The data format conventions described here shall formalize how chunks, samples, events of a sensor or another module shall be represented to be passed along the pipeline. The `BaseSource` in `base.py` implements the `_notify_all(dtype, data)` function, which has to be used for notifying subsequent modules about new data frames. All modules that observe a certain module get all `(dtype, data)`-tuples from that module and have to decide whether and how to process it.

### Conventions for `dtype` Parameter
The `dtype` parameter is an identifier for the kind of data that is offered. There are two options to declare this information:

* using a *string identifier* (**the currently preferred option**)
  * simple and flexible way for declaring data types, e.g., "mouse.pos" for the 2D mouse position on a display 
  * less powerful than using `TypeInfo`: it can provide information about either the kind of data or the sensor and it does not allow automatic dependency and type checking
* using `utils.data.TypeInfo` (experimental)
  * can be used for type matching and dependency checks (if properly defined)
  * can provide more detailed information, e.g., the kind of data such as *gaze* and the sensor name such as *pupil core*
  * introduces a larger overhead and makes maintenance more difficult
    
Both options enable subsequent processors or sinks to decide whether the accompanying `data` field should be processed or not. This also depends on the decision logic of the particular processor or sink, see the following example code:

```python
def _update_loop(self):
    while self._active:
        dtype, dataframe = self.get()
        if dtype == "mouse.pos":
            self.do_something(dataframe)
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

