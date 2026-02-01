"""Pipeline widget for interactive execution."""

import copy
from pathlib import Path
import threading
from typing import Any, Dict, Optional

import anywidget
import traitlets

from ..core import Pipeline
from ..execution import PipelineLogger
from .transport import create_transport, WidgetTransport
from ..runtime import check_colab
from ..runtime.colab import keep_alive_thread


class PipelineWidget(anywidget.AnyWidget):
    """Interactive notebook widget for executing pipelines.

    This class serves as the bridge between the Python backend execution environment
    and the React-based frontend UI. It manages:

    *   **State Syncing**: Bi-directional updates of parameters and settings via traitlets.
    *   **Execution Control**: Starting, stopping, and monitoring pipeline runs.
    *   **Output Streaming**: Sending real-time logs and status updates to the UI.
    *   **Result Handling**: Managing file downloads (supports local and Colab environments).

    **Note**: You generally do not instantiate this directly. Use
    [`create_launcher`](#pydgey.widget.create_launcher) instead.
    """

    # Frontend assets
    _esm = Path(__file__).parent / "dist" / "widget.js"

    # Schema and layout (Python -> JS)
    params_schema = traitlets.Dict().tag(sync=True)
    layout = traitlets.Dict().tag(sync=True)
    config = traitlets.Dict().tag(sync=True)

    # Parameter values (JS -> Python)
    params_values = traitlets.Dict().tag(sync=True)

    # Control signals
    run_requested = traitlets.Bool(False).tag(sync=True)
    terminate_requested = traitlets.Bool(False).tag(sync=True)
    action_requested = traitlets.Unicode("").tag(sync=True)

    # Status (Python -> JS)
    status_state = traitlets.Unicode("idle").tag(sync=True)
    status_message = traitlets.Unicode("").tag(sync=True)
    logs = traitlets.Unicode("").tag(sync=True)
    html_output = traitlets.Unicode("").tag(sync=True)
    progress = traitlets.Dict({"percent": 0, "steps": []}).tag(sync=True)

    # Results (Python -> JS)
    result_file_name = traitlets.Unicode("").tag(sync=True)
    result_file_data = traitlets.Unicode("").tag(sync=True)

    def __init__(self, pipeline: Pipeline, **kwargs: Any):
        """Initialize the widget.

        Args:
            pipeline: Pipeline instance to run.
            **kwargs: Additional traitlet values.
        """
        self.pipeline = pipeline
        self._last_result_path: Optional[str] = None

        # Get schema from pipeline
        schema = self.pipeline.get_schema()

        # Extract initial values from schema
        initial_values = self._extract_defaults(schema)

        # Set default kwargs from schema
        kwargs.setdefault("params_schema", schema.get("parameters", {}))
        kwargs.setdefault("layout", schema.get("layout", {}))
        kwargs.setdefault("config", schema.get("config", {}))
        kwargs.setdefault("params_values", initial_values)

        # Initialize progress from pipeline if available
        if hasattr(self.pipeline, "progress") and self.pipeline.progress:
            kwargs.setdefault("progress", self.pipeline.progress.to_dict())

        super().__init__(**kwargs)

        # Create transport after super().__init__ so widget is ready
        self._transport: WidgetTransport = create_transport(self)

        # Setup event handlers
        self._setup_observers()

        # Start keepalive for Colab
        if check_colab():
            keep_alive_thread()

    def _extract_defaults(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Extract default values from schema."""
        initial_values: Dict[str, Any] = {}

        # From layout (recursive)
        def extract_from_node(node: Any) -> None:
            if not isinstance(node, dict):
                return

            if node.get("type") == "field":
                props = node.get("props", {})
                name = props.get("name")
                default = props.get("default")
                if name and default is not None:
                    initial_values[name] = default

            for child in node.get("children", []):
                extract_from_node(child)

        layout = schema.get("layout")
        if layout:
            extract_from_node(layout)

        return initial_values

    def _setup_observers(self) -> None:
        """Setup event observers."""
        self.observe(self._on_run_requested, names=["run_requested"])
        self.observe(self._on_terminate_requested, names=["terminate_requested"])
        self.observe(self._on_action_requested, names=["action_requested"])
        self.on_msg(self._handle_message)

    def _on_terminate_requested(self, change: Dict[str, Any]) -> None:
        """Handle termination request."""
        if not change["new"]:
            return

        self.terminate_requested = False
        self._transport.send_logs("\n❯ Terminating pipeline...\n")
        self.pipeline.terminate()
        self.status_state = "aborted"
        self.status_message = "Terminated by user"

    def _on_run_requested(self, change: Dict[str, Any]) -> None:
        """Handle run request."""
        if not change["new"]:
            return

        self.run_requested = False
        self._start_pipeline_run()

    def _start_pipeline_run(self) -> None:
        """Start pipeline execution in a background thread."""
        self.status_state = "running"
        self.status_message = "Pipeline running..."
        self._transport.clear_logs()
        self.result_file_data = ""
        self.result_file_name = ""
        # Reset percent and set all steps to pending instantly
        # Use deepcopy to avoid mutating during frontend iteration
        current_progress = copy.deepcopy(self.progress)
        current_progress["percent"] = 0
        if "steps" in current_progress:
            for step in current_progress["steps"]:
                step["status"] = "pending"
                step["duration"] = ""
        self.progress = current_progress

        # Reset stop flag for new run
        self.pipeline._stop_requested = False

        def run_thread() -> None:
            logger = PipelineLogger(self._transport.send_logs)

            try:
                from contextlib import redirect_stderr, redirect_stdout

                with redirect_stdout(logger), redirect_stderr(logger):
                    logger.stage("Starting Pipeline")

                    # Connect progress tracker to widget traitlet
                    if hasattr(self.pipeline, "progress") and self.pipeline.progress:
                        from ..execution import Progress

                        def update_progress(p: Progress) -> None:
                            self.progress = p.to_dict()

                        self.pipeline.progress.on_update = update_progress

                    success = self.pipeline.run(self.params_values, logger)

                if success:
                    logger.success("Completed successfully!")
                    self.status_state = "finished"
                    self.status_message = "Completed successfully"
                elif getattr(self.pipeline, "_stop_requested", False):
                    logger.warning("Pipeline was terminated.")
                    self.status_state = "aborted"
                    self.status_message = "Terminated by user"
                else:
                    logger.error("Pipeline failed.")
                    self.status_state = "error"
                    self.status_message = "Failed"

            except Exception as e:
                import traceback

                self._transport.send_logs(
                    f"\n✘ Critical Exception: {e}\n{traceback.format_exc()}\n"
                )
                self.status_state = "error"
                self.status_message = f"Error: {e}"

            finally:
                # Send completion notification
                self._transport.send_message(
                    {
                        "type": "run_finished",
                        "status": self.status_state,
                        "logs": self._transport.get_logs(),
                    }
                )

                # Prepare result download if successful
                if self.status_state == "finished":
                    self._prepare_result_download(logger)

        threading.Thread(target=run_thread, daemon=True).start()

    def _prepare_result_download(self, logger: PipelineLogger) -> None:
        """Prepare result file for download.

        Checks for results in this order:
        1. Pipeline's get_result_bundle() if implemented
        2. Fallback to legacy filename patterns
        """
        try:
            # First, try the new get_result_bundle() API
            bundle = self.pipeline.get_result_bundle(self.params_values)
            if bundle is not None:
                zip_path = bundle.create_zip()
                if zip_path and zip_path.exists():
                    self._last_result_path = str(zip_path)
                    result = self._transport.prepare_download(zip_path, logger)
                    if result:
                        self.result_file_name = result["name"]
                        self.result_file_data = result["data"]
                        self._transport.send_message(
                            {
                                "type": "result_ready",
                                "name": result["name"],
                                "data": result["data"],
                            }
                        )
                    return

            # Fallback: look for legacy result zip patterns
            project_name = self.params_values.get("output_name", "project")
            zip_path = Path.cwd() / f"{project_name}_results.zip"

            if not zip_path.exists():
                prefix = self.params_values.get("output_prefix", "output")
                zip_path = Path.cwd() / f"{prefix}_results.zip"

            if zip_path.exists():
                self._last_result_path = str(zip_path)
                result = self._transport.prepare_download(zip_path, logger)
                if result:
                    self.result_file_name = result["name"]
                    self.result_file_data = result["data"]
                    self._transport.send_message(
                        {
                            "type": "result_ready",
                            "name": result["name"],
                            "data": result["data"],
                        }
                    )

        except Exception as e:
            logger.error(f"Error preparing download: {e}")

    def _handle_message(self, *args: Any) -> None:
        """Handle incoming messages from frontend.

        Note:
            Signature varies by environment:
            - Standard: (content, buffers)
            - Some environments: (widget, content, buffers)
        """
        # Extract content from variable argument list
        content: Optional[Dict[str, Any]] = None
        for arg in args:
            if isinstance(arg, dict) and "type" in arg:
                content = arg
                break

        if content is None:
            return

        msg_type = content.get("type")

        if msg_type == "poll":
            # Log polling for environments with traitlet lag
            offset = content.get("offset", 0)
            logs = self._transport.get_logs()

            msg = {
                "type": "log_batch",
                "content": logs[offset:] if offset < len(logs) else "",
                "new_offset": len(logs),
                "status": self.status_state,
            }
            self._transport.send_message(msg)

        elif msg_type == "download":
            # Native download request (Colab)
            if self._last_result_path:
                self._transport.trigger_download(self._last_result_path)

    def _on_action_requested(self, change: Dict[str, Any]) -> None:
        """Handle action request."""
        if not change["new"]:
            return

        action_name = change["new"]
        self.action_requested = ""
        self._start_action(action_name)

    def _start_action(self, action_name: str) -> None:
        """Start action execution in a background thread."""
        self.status_state = "running"
        self._transport.clear_logs()

        def action_thread() -> None:
            import time

            logger = PipelineLogger(self._transport.send_logs)
            logger.stage(f"Executing action: {action_name}")

            try:
                success = self.pipeline.handle_action(action_name, logger)
                self.status_state = "idle" if success else "error"
            except Exception as e:
                logger.error(f"Action error: {e}")
                self.status_state = "error"
            finally:
                time.sleep(0.1)  # Brief pause for log sync

                self._transport.send_message(
                    {
                        "type": "run_finished",
                        "status": self.status_state,
                        "logs": self._transport.get_logs(),
                        "result_file_name": self.result_file_name,
                        "result_file_data": self.result_file_data,
                    }
                )

        threading.Thread(target=action_thread, daemon=True).start()


def create_launcher(pipeline: Pipeline) -> PipelineWidget:
    """Create a fully configured interactive launcher widget.

    This is the main entry point for displaying your pipeline in a Jupyter environment.
    It takes a configured `Pipeline` instance and wraps it in a widget that renders
    the user interface.

    Args:
        pipeline: An instance of your custom `Pipeline` subclass.

    Returns:
        PipelineWidget: A widget instance ready to be displayed.

    Example:
        ```python
        from pydgey import create_launcher

        # Instantiate your pipeline
        pipeline = MyPipeline()

        # Create and display the widget
        widget = create_launcher(pipeline)

        # In Jupyter, this will render the UI
        widget
        ```
    """
    return PipelineWidget(pipeline)
