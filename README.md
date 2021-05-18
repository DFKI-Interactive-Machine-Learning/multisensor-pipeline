# Multisensor Pipeline (MSP)

The multisensor pipeline (`msp`) package enables stream and event processing with a small amount of dependencies. The main purpose of the `msp` pipeline is the development of research prototypes, but it can also be used for realizing small productive systems or demos that require an acquisition of multiple sensors or data streams (*source*), processing of this data(*processor*), and a utilization of the output (*sink*). The modules in a pipeline form a weakly connected directed graph. Sources and sinks are defined analogously to graph theory, processors are equivalent to internals (see this [Wikipedia article](https://en.wikipedia.org/wiki/Directed_graph#Indegree_and_outdegree)). A pipeline needs at least one source and one sink module. An `msp` pipeline can...

-   read/stream signals from any number of **source modules** like sensors, microphones, cameras, pens, eye trackers, etc.
-   flexibly process incoming data with **processor modules** (e.g. signal filtering, manipulation, and classification; signal fusion).
-   feed data streams to any number of **sink modules** for, e.g., recording data, visualizing data, or as input for user interfaces.

**What are the advantages of `msp`?** 

*   It allows setting up flexible processing pipelines with any number of sources, processors and sinks.
*   You can easily extend the pipeline by implementing [custom modules](#custom-modules).
*   Each module runs in a separate thread to ensure responsiveness.
*   Low number of dependencies = easy to integrate in your project.

# Status

[![pipeline status](https://gitlab.com/bengt/multisensor-pipeline/badges/v2.0.0-bengt-active-reading/pipeline.svg)](https://gitlab.com/bengt/multisensor-pipeline/-/commits/v2.0.0-bengt-active-reading)
[![coverage report](https://gitlab.com/bengt/multisensor-pipeline/badges/v2.0.0-bengt-active-reading/coverage.svg)](https://gitlab.com/bengt/multisensor-pipeline/-/commits/v2.0.0-bengt-active-reading)

## Hardware Requirements

This code requires a webcam to be present. To avoid using an actual device, it
can also be emulated.

Linux:

    sudo apt install --yes v4l2loopback-dkms
    sudo modprobe v4l2loopback
    ffmpeg -re -loop 1 -i data/test.png -filter:v format=yuv422p -r 30 -f v4l2 /dev/video2

## Operating Systems

We currently support Linux, Windows and macOS.

## Desktop Environments

Under Linux, we currently support the X Window System (X11), only.

## Python Versions

We currently support Python 3.6, 3.7, 3.8, and 3.9. This information might
become outdated. To be sure, check the continuous integration:

https://gitlab.com/bengt/multisensor-pipeline/-/pipelines

## Prerequisites

This package depends on PyAudio, which are bindings for portaudio19 and their 
development headers:

```shell
sudo apt install --yes --no-install-recommends gcc portaudio19-dev
```

## Installation

We recommend using an Anaconda environment with Python 3.6 (x64) or greater. To install the `multisensor_pipeline`, activate your environment of choice and run the following command:

```shell
pip install multisensor-pipeline
```

**System Requirements & Prerequisites**

* Operating System: We currently support Linux, Windows and macOS.
* Desktop Environments: Under Linux, we currently support the X Window System (X11), only.
* Python Versions: We currently support Python 3.6, 3.7, 3.8, and 3.9.
* Linux dependency: This package depends on PyAudio, which are bindings for portaudio19 and their 
development headers:
    ```shell
    sudo apt install --yes --no-install-recommends gcc portaudio19-dev
    ```

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
    -   *source >> processor*: the random arrays are sent to the array manipulator.
    -   *processor >> sink*: the manipulated arrays, i.e., the means of them, are sent to the sink module which prints them to the console.
    -   *source >> sink*: in addition, all random arrays are printed to the console.
4. Starting and stopping the pipeline: `start()` is starting all modules of the pipeline, e.g., the source starts to generate arrays now. This loop runs infinitely long and has to be stopped from outside by calling the non-blocking `stop()` function of the pipeline instance. You can wait until the pipeline has stopped using its `join()` function.  

## The MSPDataFrame Class

Instances of the `MSPDataFrame` class are used to transfer data and meta information from one module to the next.
The only required parameter is `topic: Topic` which defines what kind of data the frame delivers. The best practice is to use the factory method for this: `self._generate_topic(self, name: str, dtype: type = None)`. The actual payload can be added using keyword arguments (kwargs) when initializing an instance of `MSPDataFrame` (see `value` in the examples above). Also, you can add key-value pairs after instantiation as with any Python `dict`, because `MSPDataFrame` inherits from `dict`.

In principle, `MSPDataFrame` can carry any data type. However, the `persistence` and `networking` package requires serialization and deserialization of data frames. Currently, we support all standard data types in Python and numpy arrays (`ndarray`). Support for pillow images (`PIL.Image`) will follow.

## Custom Modules

You can easily create custom modules by inheriting from one of the abstract module classes: `BaseSource`, `BaseProcessor`, and `BaseSink`. All modules offer and/or consume data streams frame-by-frame using the `MSPDataFrame` class as data structure.

### Inherit from _BaseSource_

```python
class RandomIntSource(BaseSource):
    """ Generate 50 random numbers per second. """
       
    def on_update(self) -> Optional[MSPDataFrame]:
        sleep(.02)
        topic = self._generate_topic(name="random", dtype=int)
        return MSPDataFrame(topic=topic, value=randint(0, 100))
```

### Inherit from _BaseProcessor_

```python
class ConstraintCheckingProcessor(BaseProcessor):
    """ Checks, if incoming values are greater than 50. """

    def on_update(self, frame: MSPDataFrame) -> Optional[MSPDataFrame]:
        topic = self._generate_topic(name="constraint_check", dtype=bool)
        return MSPDataFrame(topic=topic, value=frame["value"] > 50)
```

### Inherit from _BaseSink_

```python
class ConsoleSink(BaseSink):
    """ Prints incoming frames to the console. """

    def on_update(self, frame: MSPDataFrame):
        print(frame)
```

### Using your Modules

```python
if __name__ == '__main__':
    # define the modules
    source = RandomIntSource()
    processor = ConstraintCheckingProcessor()
    sink = ConsoleSink()

    # add module to a pipeline...
    pipeline = GraphPipeline()
    pipeline.add(modules=[source, processor, sink])
    # ...and connect the modules
    pipeline.connect(module=source, successor=processor)
    pipeline.connect(module=processor, successor=sink)

    # print result of the constraint checker for 0.1 seconds
    pipeline.start()
    sleep(.1)
    pipeline.stop()
    pipeline.join()
```

You can now use your custom modules as part of a pipeline. This example connects the three sample modules using the `GraphPipeline` and executes it for 0.1 seconds. It prints the output of the `ConstraintCheckingProcessor` approximately 4 times: half of them show `value=True`, the other half shows `value=False`.
More examples can be found in the `modules` and `tests` packages.
