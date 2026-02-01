---
icon: lucide/workflow
---
# Pydgey Pipelines

The `Pipeline` class is the heart of Pydgey. It wraps your logic and configuration into a standardized application structure.

## The Basic Skeleton

Every pipeline is a Python class that inherits from `pydgey.Pipeline`. At a minimum, it must implement `define_layout` and `run`.

```python
from pydgey import Pipeline, PipelineConfig

class MyPipeline(Pipeline):
    def __init__(self):
        super().__init__(PipelineConfig(
            name="unique_id",
            title="Human Readable Title",
            subtitle="Short description appears below title"
        ))

    def define_layout(self):
        # Return a Layout object (see Layouts guide)
        pass

    def run(self, params, logger):
        # Execute logic (see Execution guide)
        return True
```

## Configuration

The `PipelineConfig` object serves as the metadata for your tool.

| Attribute | Description |
| :--- | :--- |
| `name` | **Required**. A unique identifier for the pipeline (e.g., used for generating default filenames). |
| `title` | **Required**. The main heading displayed in the widget header. |
| `subtitle` | Optional description displayed below the title. |
| `actions` | A list of custom header actions (see below). |

## Custom Actions

You can add custom action buttons to the header of your widget (e.g., "Reset", "Check Dependencies").

1.  Define the action in `PipelineConfig`.
2.  Decorate a method with `@action`.

```python
from pydgey import action

class MyPipeline(Pipeline):
    def __init__(self):
        super().__init__(PipelineConfig(
            name="demo",
            title="Demo",
            actions=["reset_defaults"]  # Define action ID here
        ))

    @action("reset_defaults")
    def reset(self, logger):
        logger.info("Resetting...")
        # Logic to reset state
        return True
```

## Lifecycle Hooks

Pydgey manages the lifecycle of your pipeline automatically.

1.  **__init__**: Called when you instantiate the class in the notebook.
2.  **define_layout**: Called immediately to build the frontend schema.
3.  **run**: Called when the user clicks the "Run Pipeline" button.
4.  **terminate**: Called when the user clicks "Abort" or interrupts the kernel.
5.  **get_result_bundle**: Called after a successful run to determining what files to let the user download.

### Cleanup & Termination

If your pipeline performs long-running tasks, you should handle termination gracefully.

```python
def run(self, params, logger):
    for i in range(100):
        if self.is_stopped:  # Check the stop flag
            logger.warning("Aborted by user")
            return False
            
        # Do work...
```

See the **[Execution](execution.md)** guide for detailed patterns on handling subprocesses and cancellation.
