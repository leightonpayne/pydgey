"""Progress tracking for pipeline execution."""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
import time


@dataclass
class Step:
    """A single step in a pipeline execution."""

    name: str
    status: str = "pending"  # pending, running, completed, failed, skipped
    message: str = ""
    started_at: Optional[float] = None
    completed_at: Optional[float] = None

    @property
    def duration(self) -> Optional[float]:
        """Get step duration in seconds."""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        elif self.started_at:
            return time.time() - self.started_at
        return None

    @property
    def duration_human(self) -> str:
        """Get human-readable duration."""
        d = self.duration
        if d is None:
            return ""
        if d < 60:
            return f"{d:.1f}s"
        elif d < 3600:
            return f"{d / 60:.1f}m"
        else:
            return f"{d / 3600:.1f}h"


@dataclass
class Progress:
    """Track progress through a multi-step pipeline.

    Example:
        progress = Progress([
            "Load Data",
            "Process",
            "Generate Report",
        ])

        with progress.step("Load Data") as step:
            # Do work...
            step.message = "Loaded 100 records"

        progress.skip("Process", "No processing needed")

        with progress.step("Generate Report"):
            # Do work...
            pass
    """

    steps: List[Step] = field(default_factory=list)
    on_update: Optional[Callable[["Progress"], None]] = None
    _current_step: Optional[Step] = None

    def __init__(
        self,
        step_names: Optional[List[str]] = None,
        on_update: Optional[Callable[["Progress"], None]] = None,
    ):
        """Initialize progress tracker.

        Args:
            step_names: List of step names to pre-define.
            on_update: Callback called when progress changes.
        """
        self.steps = []
        self.on_update = on_update
        self._current_step = None

        if step_names:
            for name in step_names:
                self.steps.append(Step(name=name))

    def add_step(self, name: str) -> Step:
        """Add a new step.

        Args:
            name: Step name.

        Returns:
            The created step.
        """
        step = Step(name=name)
        self.steps.append(step)
        self._notify()
        return step

    def step(self, name: str) -> "StepContext":
        """Get a context manager for a step.

        Args:
            name: Step name (must exist or will be created).

        Returns:
            Context manager for the step.
        """
        # Find or create step
        step = self._get_step(name)
        if step is None:
            step = self.add_step(name)
        return StepContext(self, step)

    def start(self, name: str, message: str = "") -> Step:
        """Mark a step as started.

        Args:
            name: Step name.
            message: Optional status message.

        Returns:
            The step.
        """
        step = self._get_step(name)
        if step:
            step.status = "running"
            step.message = message
            step.started_at = time.time()
            self._current_step = step
            self._notify()
        return step

    def complete(self, name: str, message: str = "") -> Step:
        """Mark a step as completed.

        Args:
            name: Step name.
            message: Optional completion message.

        Returns:
            The step.
        """
        step = self._get_step(name)
        if step:
            step.status = "completed"
            step.message = message
            step.completed_at = time.time()
            if self._current_step == step:
                self._current_step = None
            self._notify()
        return step

    def fail(self, name: str, message: str = "") -> Step:
        """Mark a step as failed.

        Args:
            name: Step name.
            message: Error message.

        Returns:
            The step.
        """
        step = self._get_step(name)
        if step:
            step.status = "failed"
            step.message = message
            step.completed_at = time.time()
            if self._current_step == step:
                self._current_step = None
            self._notify()
        return step

    def skip(self, name: str, message: str = "") -> Step:
        """Mark a step as skipped.

        Args:
            name: Step name.
            message: Reason for skipping.

        Returns:
            The step.
        """
        step = self._get_step(name)
        if step:
            step.status = "skipped"
            step.message = message
            self._notify()
        return step

    @property
    def current(self) -> Optional[Step]:
        """Get the currently running step."""
        return self._current_step

    @property
    def completed_count(self) -> int:
        """Count of completed steps."""
        return len([s for s in self.steps if s.status == "completed"])

    @property
    def total_count(self) -> int:
        """Total number of steps."""
        return len(self.steps)

    @property
    def percent(self) -> float:
        """Completion percentage (0-100)."""
        if not self.steps:
            return 0
        return (self.completed_count / self.total_count) * 100

    @property
    def is_complete(self) -> bool:
        """Check if all steps are done (completed, failed, or skipped)."""
        return all(s.status in ("completed", "failed", "skipped") for s in self.steps)

    @property
    def has_failures(self) -> bool:
        """Check if any step failed."""
        return any(s.status == "failed" for s in self.steps)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "steps": [
                {
                    "name": s.name,
                    "status": s.status,
                    "message": s.message,
                    "duration": s.duration_human,
                }
                for s in self.steps
            ],
            "current": self._current_step.name if self._current_step else None,
            "percent": self.percent,
            "completed": self.completed_count,
            "total": self.total_count,
        }

    def _get_step(self, name: str) -> Optional[Step]:
        """Find a step by name."""
        for step in self.steps:
            if step.name == name:
                return step
        return None

    def _notify(self) -> None:
        """Call the update callback if set."""
        if self.on_update:
            self.on_update(self)


class StepContext:
    """Context manager for step execution."""

    def __init__(self, progress: Progress, step: Step):
        self.progress = progress
        self.step = step

    def __enter__(self) -> Step:
        self.step.status = "running"
        self.step.started_at = time.time()
        self.progress._current_step = self.step
        self.progress._notify()
        return self.step

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_type is not None:
            self.step.status = "failed"
            self.step.message = str(exc_val)
        else:
            self.step.status = "completed"

        self.step.completed_at = time.time()
        if self.progress._current_step == self.step:
            self.progress._current_step = None
        self.progress._notify()

        return False  # Don't suppress exceptions
