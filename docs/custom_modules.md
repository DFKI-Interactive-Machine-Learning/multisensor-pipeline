
## Custom Modules
You can easily create custom modules by inheriting from one of the abstrac module classes: `BaseSource`, `BaseProcessor`, and `BaseSink`. All modules offer and/or consume data streams frame-by-frame using the `MSPDataFrame` class as data structure.

### Inherit from _BaseSource_
```python
class RandomIntSource(BaseSource):
    """Generate 50 random numbers per second."""
       
    def on_update(self) -> Optional[MSPDataFrame]:
        sleep(.02)
        topic = self._generate_topic(name="random", dtype=int)
        return MSPDataFrame(topic=topic, value=randint(0, 100))
```

### Inherit from _BaseProcessor_
```python
class ConstraintCheckingProcessor(BaseProcessor):
    """Check, if incoming values are greater than 50."""

    def on_update(self, frame: MSPDataFrame) -> Optional[MSPDataFrame]:
        topic = self._generate_topic(name="constraint_check", dtype=bool)
        return MSPDataFrame(topic=topic, value=frame["value"] > 50)
```

### Inherit from _BaseSink_
```python
class ConsoleSink(BaseSink):
    """Print incoming frames to the console."""

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
Further examples can be found in the `modules` and `tests` packages.
 
