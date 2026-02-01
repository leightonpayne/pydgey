"""Transport layer for widget communication.

Abstracts environment-specific communication (Colab vs standard Jupyter).
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional, TYPE_CHECKING
import base64
import threading

if TYPE_CHECKING:
    from .widget import PipelineWidget


class WidgetTransport(ABC):
    """Abstract base for widget-backend communication.

    Different environments (Colab, JupyterLab, VS Code) have different
    quirks in how traitlets sync and how file downloads work.
    """

    @abstractmethod
    def send_logs(self, logs: str) -> None:
        """Send log content to the frontend."""
        pass

    @abstractmethod
    def send_message(self, message: Dict[str, Any]) -> None:
        """Send a custom message to the frontend."""
        pass

    @abstractmethod
    def prepare_download(
        self,
        file_path: Path,
        logger: Any,
        max_size_mb: float = 50.0,
    ) -> Optional[Dict[str, str]]:
        """Prepare a file for download.

        Args:
            file_path: Path to the file to download.
            logger: Logger for status messages.
            max_size_mb: Maximum file size for base64 encoding.

        Returns:
            Dict with 'name' and 'data' keys, or None if file too large.
        """
        pass

    @abstractmethod
    def trigger_download(self, file_path: str) -> bool:
        """Trigger a native file download if available.

        Args:
            file_path: Path to the file to download.

        Returns:
            True if native download was triggered, False otherwise.
        """
        pass


class StandardTransport(WidgetTransport):
    """Standard Jupyter transport using traitlets."""

    def __init__(self, widget: "PipelineWidget") -> None:
        self.widget = widget
        self._log_lock = threading.Lock()
        self._log_history = ""

    def send_logs(self, logs: str) -> None:
        """Append logs and sync to widget traitlet."""
        with self._log_lock:
            self._log_history += logs
            self.widget.logs = self._log_history

            # Proactively push logs to frontend to ensure real-time updates
            # This bypasses traitlet sync lag and works even if polling fails
            self.widget.send(
                {
                    "type": "log_batch",
                    "content": logs,
                    "status": getattr(self.widget, "status_state", "running"),
                }
            )

    def get_logs(self) -> str:
        """Get full log history."""
        with self._log_lock:
            return self._log_history

    def clear_logs(self) -> None:
        """Clear log history."""
        with self._log_lock:
            self._log_history = ""
            self.widget.logs = ""

    def send_message(self, message: Dict[str, Any]) -> None:
        """Send a custom message via widget.send()."""
        self.widget.send(message)

    def prepare_download(
        self,
        file_path: Path,
        logger: Any,
        max_size_mb: float = 50.0,
    ) -> Optional[Dict[str, str]]:
        """Prepare file for download via base64 encoding."""
        if not file_path.exists():
            return None

        size_mb = file_path.stat().st_size / (1024 * 1024)

        if size_mb > max_size_mb:
            logger.warning(
                f"File is too large ({size_mb:.1f}MB) for widget download. "
                "Please use file explorer."
            )
            return None

        with open(file_path, "rb") as f:
            b64_data = base64.b64encode(f.read()).decode("utf-8")

        # Determine MIME type
        suffix = file_path.suffix.lower()
        mime_types = {
            ".zip": "application/zip",
            ".gz": "application/gzip",
            ".tar": "application/x-tar",
            ".pdf": "application/pdf",
            ".txt": "text/plain",
            ".csv": "text/csv",
            ".json": "application/json",
        }
        mime_type = mime_types.get(suffix, "application/octet-stream")

        return {
            "name": file_path.name,
            "data": f"data:{mime_type};base64,{b64_data}",
        }

    def trigger_download(self, file_path: str) -> bool:
        """Standard transport has no native download - return False."""
        return False


class ColabTransport(StandardTransport):
    """Google Colab transport with workarounds for traitlet sync issues."""

    def send_message(self, message: Dict[str, Any]) -> None:
        """Send message with Colab-specific handling.

        Colab has traitlet sync lag, so we also store results locally.
        """
        super().send_message(message)

        # Store result data for native download fallback
        if message.get("type") == "result_ready":
            self._last_result_name = message.get("name")
            self._last_result_data = message.get("data")

    def trigger_download(self, file_path: str) -> bool:
        """Use google.colab.files.download() for native download."""
        try:
            from google.colab import files

            files.download(file_path)
            return True
        except ImportError:
            return False
        except Exception:
            return False


def create_transport(widget: Any) -> WidgetTransport:
    """Factory to create appropriate transport for current environment.

    Args:
        widget: The PipelineWidget instance.

    Returns:
        Appropriate transport for the current environment.
    """
    import sys

    if "google.colab" in sys.modules:
        return ColabTransport(widget)
    else:
        return StandardTransport(widget)
