# pipeline_ui

A Python framework for building sleek, modular interactive widgets for running command-line tools and pipelines in Jupyter notebooks and Google Colab.

## Features

- **Declarative UI**: Define your interface using a clean Layout/Field DSL
- **Interactive Widgets**: Real-time parameter editing with live validation
- **Progress Tracking**: Built-in progress indicators for multi-step pipelines
- **Environment Adaptive**: Works seamlessly in Jupyter, VS Code, and Google Colab
- **Result Handling**: Automatic result bundling and download support
- **Type-Safe Params**: Optional typed parameter access with dataclasses

## Quick Start

```python
from pipeline_ui import Pipeline, Layout, Field, create_launcher

class MyPipeline(Pipeline):
    def define_layout(self):
        return Layout.Page([
            Layout.Section("Settings", [
                Field.Text("name", "Project Name", default="my_project"),
                Field.Int("threads", "CPU Threads", default=4, min=1, max=32),
                Field.Switch("verbose", "Verbose Output", default=False),
            ])
        ])
    
    def run(self, params, logger):
        logger.info(f"Running {params['name']} with {params['threads']} threads")
        # Your pipeline logic here
        return True

# Display the widget
widget = create_launcher(MyPipeline())
widget
```

## Installation

```bash
pip install pipeline_ui
# or
conda install -c conda-forge pipeline_ui
```

## Core Concepts

### Pipeline

The base class for all pipelines. Subclass and implement:

- `define_layout()`: Define the UI structure
- `run(params, logger)`: Execute the pipeline
- `define_parameters()` (optional): Define legacy parameters

### Layout DSL

Build your UI declaratively:

```python
Layout.Page([
    Layout.Tabs([
        Layout.Tab("Input", [
            Field.File("input", "Input File", accept=[".fastq", ".fq.gz"]),
        ]),
        Layout.Tab("Settings", [
            Layout.Section("Performance", [
                Field.Int("cpu", "CPU Cores", default=4),
            ]),
            Layout.Section("Advanced", [
                Field.Switch("debug", "Debug Mode"),
            ], collapsed=True),
        ]),
    ])
])
```

### Field Types

- `Field.Text()` - Single-line text input
- `Field.TextArea()` - Multi-line text input
- `Field.Int()` - Integer input with min/max
- `Field.Float()` - Decimal input with step
- `Field.Switch()` - Boolean toggle
- `Field.Select()` - Dropdown selection
- `Field.MultiSelect()` - Multiple selection
- `Field.File()` - File upload

### Validators

Add validation rules to fields:

```python
from pipeline_ui import Validators

Field.Text("email", "Email", 
    validators=[Validators.required(), Validators.email()])

Field.Int("port", "Port", 
    validators=[Validators.range(1, 65535)])
```

### Conditional Visibility

Show/hide fields based on other values:

```python
Field.Switch("advanced", "Show Advanced"),
Field.Int("custom", "Custom Value", 
    visible_when=("advanced", "==", True))
```

### Components Library

Pre-built UI patterns:

```python
from pipeline_ui import Components

Components.FileInput("reads", "FASTQ", accept=[".fq.gz"])
Components.OutputConfig(include_directory=True)
Components.PerformanceSettings(cpu_default=8)
```

### Progress Tracking

Track multi-step execution:

```python
from pipeline_ui import Progress

def run(self, params, logger):
    progress = Progress(["Load", "Process", "Save"])
    
    with progress.step("Load"):
        data = load_data(params["input"])
    
    with progress.step("Process"):
        result = process(data)
    
    with progress.step("Save"):
        save(result)
    
    return True
```

### Dependency Checking

Verify required tools:

```python
from pipeline_ui import DependencyChecker, require_tool

# Quick check
require_tool("hmmsearch", install_hint="conda install hmmer")

# Full check
checker = DependencyChecker()
checker.add("HMMER", "hmmsearch")
checker.add("BLAST+", "blastp")
result = checker.check()
result.raise_if_missing()
```

### Typed Parameters

Type-safe parameter access:

```python
from dataclasses import dataclass
from pipeline_ui import ParamsBase

@dataclass
class MyParams(ParamsBase):
    threads: int = 4
    output: str = "results"
    verbose: bool = False

def run(self, params_dict, logger):
    params = MyParams.from_dict(params_dict)
    logger.info(f"Using {params.threads} threads")
```

### Result Bundling

Package results for download:

```python
from pipeline_ui import ResultBundle

bundle = ResultBundle("analysis")
bundle.add_file("output.txt", description="Main results")
bundle.add_directory("plots/", pattern="*.png")
zip_path = bundle.create_zip()
```

## API Reference

### Core

| Class | Description |
|-------|-------------|
| `Pipeline` | Abstract base class for pipelines |
| `PipelineConfig` | Configuration for pipeline metadata |
| `PipelineParameter` | Legacy parameter definition |

### Decorators

| Decorator | Description |
|-----------|-------------|
| `@action` | Mark a method as a UI action button |
| `@parameter` | Define a parameter inline |

### Layout

| Class | Description |
|-------|-------------|
| `Layout` | Factory for container elements |
| `Field` | Factory for form fields |
| `UIElement` | Base element class |
| `Validators` | Factory for validation rules |

### Utilities

| Function/Class | Description |
|----------------|-------------|
| `run_command()` | Execute shell commands with logging |
| `PipelineLogger` | Rich logging with stages/steps |
| `Progress` | Multi-step progress tracking |
| `ResultBundle` | Result file packaging |
| `DependencyChecker` | Tool availability checking |

### Errors

| Exception | Description |
|-----------|-------------|
| `PipelineError` | Base exception |
| `ValidationError` | Parameter validation failed |
| `DependencyError` | Missing required tool |
| `ExecutionError` | Pipeline execution failed |

## License

MIT License
