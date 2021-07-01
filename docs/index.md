# Overview
The multisensor pipeline (`msp`) package enables stream and event processing with a small amount of dependencies. The main purpose of the `msp` pipeline is the development of research prototypes, but it can also be used for realizing small productive systems or demos that require an acquisition of multiple sensors or data streams (*source*), processing of this data(*processor*), and a utilization of the output (*sink*). The modules in a pipeline form a weakly connected directed graph. Sources and sinks are defined analogously to graph theory, processors are equivalent to internals (see this [Wikipedia article](https://en.wikipedia.org/wiki/Directed_graph#Indegree_and_outdegree)). A pipeline needs at least one source and one sink module. An `msp` pipeline can...

- read/stream signals from any number of **source modules** like sensors, microphones, cameras, pens, eye trackers, etc.
- flexibly process incoming data with **processor modules** (e.g. signal filtering, manipulation, and classification; signal fusion).
- feed data streams to any number of **sink modules** for, e.g., recording data, visualizing data, or as input for user interfaces.

**What are the advantages of `msp`?** 

* It allows to setup flexible processing pipelines with any number of sources, processors and sinks.
* You can easily extend the pipeline by implementing [custom modules](custom-modules).
* Each module runs in a separate thread to ensure responsiveness.
* Low number of dependecies = easy to integrate in your project.


## Quick Installation
We recommend to use an Anaconda environment with Python 3.6 (x64) or greater. To install the `multisensor_pipeline`, activate your environment of choice and run the following command:

```shell
pip install multisensor-pipeline
```
You can also install the package from source:
Please see the [Installation](installation.md) for further details.

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
