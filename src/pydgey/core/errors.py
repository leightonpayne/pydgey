"""Error types for pipeline execution."""

from typing import Any, Dict, List, Optional


class PipelineError(Exception):
    """Base exception for pipeline errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ValidationError(PipelineError):
    """Raised when parameter validation fails."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        errors: Optional[List[Dict[str, str]]] = None,
    ):
        """Initialize validation error.

        Args:
            message: Error message.
            field: Field that failed validation.
            errors: List of field errors with 'field' and 'message' keys.
        """
        super().__init__(message, {"field": field, "errors": errors})
        self.field = field
        self.errors = errors or []

    @classmethod
    def from_fields(cls, field_errors: Dict[str, str]) -> "ValidationError":
        """Create from a dict of field -> error message.

        Args:
            field_errors: Dict mapping field names to error messages.

        Returns:
            ValidationError with all field errors.
        """
        errors = [{"field": k, "message": v} for k, v in field_errors.items()]
        return cls(
            f"Validation failed for {len(errors)} field(s)",
            errors=errors,
        )


class DependencyError(PipelineError):
    """Raised when a required dependency is missing."""

    def __init__(
        self,
        message: str,
        tool: Optional[str] = None,
        install_hint: Optional[str] = None,
    ):
        """Initialize dependency error.

        Args:
            message: Error message.
            tool: Name of the missing tool.
            install_hint: Hint for how to install.
        """
        super().__init__(message, {"tool": tool, "install_hint": install_hint})
        self.tool = tool
        self.install_hint = install_hint


class ExecutionError(PipelineError):
    """Raised when pipeline execution fails."""

    def __init__(
        self,
        message: str,
        step: Optional[str] = None,
        exit_code: Optional[int] = None,
        stderr: Optional[str] = None,
    ):
        """Initialize execution error.

        Args:
            message: Error message.
            step: Step that failed.
            exit_code: Process exit code if applicable.
            stderr: Standard error output.
        """
        super().__init__(
            message,
            {"step": step, "exit_code": exit_code, "stderr": stderr},
        )
        self.step = step
        self.exit_code = exit_code
        self.stderr = stderr


class ConfigurationError(PipelineError):
    """Raised when pipeline configuration is invalid."""

    pass


class FileNotFoundPipelineError(PipelineError):
    """Raised when a required file is not found.

    Note:
        Named to avoid shadowing the builtin FileNotFoundError.
    """

    def __init__(self, message: str, path: str):
        """Initialize file not found error.

        Args:
            message: Error message.
            path: Path to the missing file.
        """
        super().__init__(message, {"path": path})
        self.path = path


class TimeoutPipelineError(PipelineError):
    """Raised when an operation times out.

    Note:
        Named to avoid shadowing the builtin TimeoutError.
    """

    def __init__(self, message: str, timeout_seconds: float):
        """Initialize timeout error.

        Args:
            message: Error message.
            timeout_seconds: The timeout that was exceeded.
        """
        super().__init__(message, {"timeout_seconds": timeout_seconds})
        self.timeout_seconds = timeout_seconds
