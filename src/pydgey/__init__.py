"""pydgey - Interactive widgets for tools and pipelines.

A framework for building sleek, modular interactive widgets for
setting parameters and running command-line tools and pipelines.

Example:
    ```python
    from pydgey import Pipeline, Layout, Field, create_launcher

    class MyPipeline(Pipeline):
        def define_layout(self):
            return Layout.Page([
                Layout.Section("Settings", [
                    Field.Text("name", "Project Name", default="my_project"),
                    Field.Int("threads", "Threads", default=4),
                ])
            ])

        def run(self, params, logger):
            logger.info(f"Running {params['name']}")
            return True

    # Display widget
    widget = create_launcher(MyPipeline())
    ```
"""

# Core abstractions
from .core import (
    Pipeline,
    PipelineConfig,
    action,
    ParamsBase,
    typed_params,
    PipelineError,
    ValidationError,
    DependencyError,
    ExecutionError,
    ConfigurationError,
)

# Widget
from .widget import PipelineWidget, create_launcher

# Layout DSL
from .layout import (
    Layout,
    Field,
    UIElement,
    Validator,
    Validators,
    Components,
)

# Runtime utilities
from .runtime import (
    run_command,
    check_colab,
    check_environment,
    check_tool,
    setup_environment,
    PixiEnvironment,
    mount_google_drive,
)

# Execution utilities
from .execution import (
    PipelineLogger,
    Progress,
    Step,
    ResultBundle,
    ResultFile,
)

__version__ = "0.3.0"

__all__ = [
    # Core
    "Pipeline",
    "PipelineConfig",
    "action",
    "ParamsBase",
    "typed_params",
    # Widget
    "PipelineWidget",
    "create_launcher",
    # Layout
    "Layout",
    "Field",
    "UIElement",
    "Validator",
    "Validators",
    "Components",
    # Runtime
    "run_command",
    "check_colab",
    "check_environment",
    "check_tool",
    "setup_environment",
    "PixiEnvironment",
    "mount_google_drive",
    # Execution
    "PipelineLogger",
    "Progress",
    "Step",
    "ResultBundle",
    "ResultFile",
    # Errors
    "PipelineError",
    "ValidationError",
    "DependencyError",
    "ExecutionError",
    "ConfigurationError",
]
