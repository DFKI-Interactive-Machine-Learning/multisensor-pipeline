# Multisensor Pipeline (MSP) [![Python package](https://github.com/DFKI-Interactive-Machine-Learning/multisensor-pipeline/actions/workflows/python-package.yml/badge.svg)](https://github.com/DFKI-Interactive-Machine-Learning/multisensor-pipeline/actions/workflows/python-package.yml)

The multisensor pipeline (`msp`) package enables stream and event processing with a small amount of dependencies. The main purpose of the `msp` pipeline is the development of research prototypes, but it can also be used for realizing small productive systems or demos that require acquisition of samples from multiple sensor or data streams (via *source* modules), processing of these samples (via *processor* modules), and a utilization of the output (via *sink* modules). Modules can be connected to a pipeline which is represented as a weakly connected directed graph. Sources and sinks are defined analogously to graph theory, processors are equivalent to internals (see this [Wikipedia article](https://en.wikipedia.org/wiki/Directed_graph#Indegree_and_outdegree)). A pipeline needs at least one source and one sink module. An `msp` pipeline can...

-   read/stream signals from any number of **source modules** like sensors, microphones, cameras, pens, eye trackers, etc.
-   flexibly process incoming data with **processor modules** (e.g. signal filtering, manipulation, and classification; signal fusion).
-   feed data streams to any number of **sink modules** for, e.g., recording data, visualizing data, or as input for user interfaces.

**What are the advantages of `msp`?** 

*   It enables setting up flexible processing pipelines with any number of sources, processors and sinks.
*   You can easily extend the pipeline by implementing [custom modules](#custom-modules).
*   Each module runs in a separate thread to ensure responsiveness.
*   Low number of dependencies = easy to integrate in your project.

## Installation

We recommend using an Anaconda environment with Python >= 3.6. To install the `multisensor_pipeline`, activate your environment of choice and run the following command:

```shell
pip install multisensor-pipeline
```

## Quick Start Example

```python
from multisensor_pipeline import GraphPipeline
from multisensor_pipeline.modules.npy import RandomArraySource, ArrayManipulationProcessor
from multisensor_pipeline.modules import ConsoleSink
from time import sleep
import numpy as np

# define the modules
source = RandomArraySource(shape=(50,), samplerate=60)
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

# print means of random numbers for 0.1 seconds
pipeline.start()
sleep(.1)
pipeline.stop()
pipeline.join()
```

The example initializes three modules, one source, one processor and one sink. The `RandomArraySource` generates numpy arrays (ndarray) with random numbers 60 times per second. Each array contains 50 random numbers (shape). The `ArrayManipulationProcessor` takes an array as input, computes the mean of it, and provides it to registered observers. The `ConsoleSink` prints all incoming messages to the console. 

The example contains four major steps:
 
1.  All modules are created and parametrized
2.  The pipeline is created and all modules are added to it.
3.  The modules are connected to build the multisensor pipeline. This step defines what your pipeline is going to do and, therefore, is the most important step.
    -   *source >> processor*: the random arrays are sent to the array manipulator.
    -   *processor >> sink*: the manipulated arrays, i.e., their means, are sent to the sink module which prints them to the console.
    -   *source >> sink*: in addition, all random arrays are printed to the console.
4. Starting and stopping the pipeline: `start()` is starting all modules of the pipeline, e.g., the source starts to generate arrays now. This loop runs infinitely long and has to be stopped from outside by calling the non-blocking `stop()` function of the pipeline. You can wait until the pipeline has stopped using its `join()` function.  

## The MSPDataFrame Class

Instances of the `MSPDataFrame` class are used to transfer data and meta information from one module to the next.
The `topic: Topic` of a dataframe defines what kind of data the frame delivers. It can have a `name: str` and a `dtype: type`. The payload is contained in the `data` field.

In principle, `MSPDataFrame` can carry any data type in `data`. However, the `persistence` and `networking` packages require serialization and deserialization of dataframes. Currently, we support all standard data types of Python, numpy arrays (`ndarray`), and pillow images (`PIL.Image`) based on the *msgpack* library.

## Custom Modules

You can easily create custom modules by inheriting from one of the abstract module classes: `BaseSource`, `BaseProcessor`, and `BaseSink`. All modules offer and/or consume data streams frame-by-frame using the `MSPDataFrame` class as data structure. We provide a few simple examples and show how they work together in a pipeline:

### Inherit from _BaseSource_

```python
class RandomIntSource(BaseSource):
    """Generate 50 random integer numbers per second."""

    def on_update(self) -> Optional[MSPDataFrame]:
        sleep(.02)
        return MSPDataFrame(topic=self.output_topics[0], data=randint(0, 100))

    @property
    def output_topics(self) -> Optional[List[Topic]]:
        return [Topic(name='random', dtype=int)]
```

### Inherit from _BaseProcessor_

```python
class ConstraintCheckingProcessor(BaseProcessor):
    """Checks, if incoming integer values are greater than 50."""

    def on_update(self, frame: MSPDataFrame) -> Optional[MSPDataFrame]:
        return MSPDataFrame(topic=self.output_topics[0], data=frame.data > 50)

    @property
    def input_topics(self) -> List[Topic]:
        return [Topic(dtype=int)]

    @property
    def output_topics(self) -> Optional[List[Topic]]:
        return [Topic(name='constraint_check', dtype=bool)]
```

### Inherit from _BaseSink_

```python
class ConsoleSink(BaseSink):
    """ Prints incoming frames to the console. """

    def on_update(self, frame: MSPDataFrame):
        if frame is not None:
            print(f"{frame.timestamp}\t{frame.topic}\t{frame.data}")
```

### Using the Modules

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

You can now use the custom modules in a pipeline. The example above connects the three sample modules using the `GraphPipeline` and executes it for 0.1 seconds. The output of the `ConstraintCheckingProcessor` should look like this:

```shell
1639412295.2498586	<class 'bool'>:constraint_check	False
1639412295.2803597	<class 'bool'>:constraint_check	False
1639412295.3114836	<class 'bool'>:constraint_check	False
1639412295.342433	<class 'bool'>:constraint_check	True
```

More examples can be found in the `tests` packages.
Please note that you can define input and output topics. If you do so, the pipeline will automatically reduce traffic to supported topics. Setting the name or dtype of a Topic instance to None corresponds to a whitespace. For instance, the `ConstraintCheckingProcessor` will try to process all dataframes with `topic.dtype==int`, the topic name does not matter in this case.

## Cite Us
Please cite the following paper when using the multisensor-pipeline in your project:

```
@inproceedings{barz_multisensor-pipeline_2021,
    author = {Barz, Michael and Bhatti, Omair Shahzad and L\"{u}ers, Bengt and Prange, Alexander and Sonntag, Daniel},
    title = {Multisensor-Pipeline: A Lightweight, Flexible, and Extensible Framework for Building Multimodal-Multisensor Interfaces},
    year = {2021},
    isbn = {9781450384711},
    publisher = {Association for Computing Machinery},
    address = {New York, NY, USA},
    url = {https://doi.org/10.1145/3461615.3485432},
    doi = {10.1145/3461615.3485432},
    booktitle = {Companion Publication of the 2021 International Conference on Multimodal Interaction},
    pages = {13–18},
    numpages = {6},
    keywords = {open source framework, stream processing, eye tracking, computer vision, prototyping, multimodal-multisensor interfaces},
    location = {Montreal, QC, Canada},
    series = {ICMI '21 Companion}
}
```
