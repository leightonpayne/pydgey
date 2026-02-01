"""Abstract base class for pipelines."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
from pathlib import Path

from .config import PipelineConfig

if TYPE_CHECKING:
    from ..logging import PipelineLogger
    from ..results import ResultBundle

import subprocess


class Pipeline(ABC):
    """Abstract base class for a pipeline.

    Subclass this to create your own pipeline with custom parameters,
    layout, and execution logic.

    Example:
        ```python
        class MyPipeline(Pipeline):
            def __init__(self):
                config = PipelineConfig(
                    name="MyPipeline",
                    title="My Pipeline",
                    subtitle="Does something useful",
                )
                super().__init__(config)

            def define_layout(self):
                return Layout.Page([
                    Field.Text("input", "Input File"),
                    Field.Int("threads", "Threads", default=4),
                ])

            def run(self, params, logger):
                logger.info(f"Running with {params['threads']} threads")
                return True
        ```
    """

    def __init__(self, config: Optional[PipelineConfig] = None):
        """Initialize the pipeline.

        Args:
            config: Pipeline configuration. If None, uses defaults.
        """
        self.config = config or PipelineConfig()
        self._stop_requested = False
        self._active_process: "subprocess.Popen | None" = None

    def define_layout(self) -> Optional[Any]:
        """Define the UI layout for this pipeline.

        Override this to return a Layout object for custom UI arrangement.

        Returns:
            Layout object.
        """
        return None

    @abstractmethod
    def run(self, params: Dict[str, Any], logger: "PipelineLogger") -> bool:
        """Run the pipeline with the given parameters.

        Args:
            params: Dictionary of parameter values from the UI.
            logger: PipelineLogger for output.

        Returns:
            True if successful, False otherwise.
        """
        pass

    def terminate(self) -> None:
        """Terminate a running pipeline.

        Sets the stop flag and kills any active subprocess.
        Subclasses can override for additional cleanup.
        """
        self._stop_requested = True
        if self._active_process and self._active_process.poll() is None:
            self._active_process.terminate()
            try:
                self._active_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self._active_process.kill()

    @property
    def is_stopped(self) -> bool:
        """Check if the pipeline has been requested to stop.

        Use this in your run() method to check for abort requests:

            if self.is_stopped:
                return False
        """
        return self._stop_requested

    def register_process(self, process: "subprocess.Popen") -> None:
        """Register a subprocess for abort handling.

        Call this when starting a subprocess so terminate() can kill it:

            process = subprocess.Popen([...])
            self.register_process(process)
        """
        self._active_process = process

    def run_command(
        self,
        command: Union[str, List[str]],
        logger: "PipelineLogger",
        cwd: Optional[Union[str, Path]] = None,
    ) -> int:
        """Run a command with automatic abort handling.

        This wraps the run_command utility with the pipeline's stop checking
        and process registration, so abort will immediately kill the process.

        Args:
            command: Command string or list of arguments.
            logger: PipelineLogger for output.
            cwd: Optional working directory.

        Returns:
            Exit code (0 = success, -1 = aborted, 1+ = error).

        Example:
            ```python
            exit_code = self.run_command("ls -la", logger)
            if exit_code != 0:
                return False
            ```
        """
        from ..commands import run_command as _run_command

        return _run_command(
            command=command,
            logger=logger,
            stop_check=lambda: self._stop_requested,
            on_process_start=self.register_process,
            cwd=cwd,
        )

    def get_result_bundle(self, params: Dict[str, Any]) -> Optional["ResultBundle"]:
        """Declare result files for download after successful execution.

        Override this to return a ResultBundle containing output files.
        The widget will automatically package and offer these for download.

        Args:
            params: The parameter values used for the run.

        Returns:
            ResultBundle containing output files, or None if no results.

        Example:
            ```python
            def get_result_bundle(self, params):
                bundle = ResultBundle(params["output_name"])
                bundle.add_file("output.txt", description="Main output")
                bundle.add_directory("plots/", description="Generated plots")
                return bundle
            ```
        """
        return None

    def handle_action(self, action_name: str, logger: "PipelineLogger") -> bool:
        """Handle a custom action triggered from the UI.

        Automatically dispatches to methods decorated with @action(name).

        Args:
            action_name: Name of the action to handle.
            logger: PipelineLogger for output.

        Returns:
            True if action succeeded, False otherwise.
        """
        # Find method decorated with @action(action_name)
        for attr_name in dir(self):
            try:
                attr = getattr(self, attr_name)
                if callable(attr) and getattr(attr, "_is_action", False):
                    if getattr(attr, "_action_name") == action_name:
                        return attr(logger)
            except Exception:
                continue

        logger.warning(f"No handler for action: {action_name}")
        return False

    def get_schema(self) -> Dict[str, Any]:
        """Get the full schema to send to the widget.

        Returns:
            Dictionary with parameters, layout, and config for the frontend.
        """
        layout = self.define_layout()
        layout_dict = layout.to_dict() if layout else None

        return {
            "parameters": {},  # Legacy support removed
            "layout": layout_dict,
            "config": {
                "name": self.config.name,
                "title": self.config.title,
                "subtitle": self.config.subtitle,
                "actions": self.config.actions,
            },
        }
