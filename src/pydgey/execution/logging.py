import sys
from typing import Callable, Optional
from rich.console import Console
from rich.theme import Theme

# Define professional theme
PIPELINE_THEME = Theme(
    {
        "info": "dim white",
        "success": "bold green",
        "warning": "bold yellow",
        "error": "bold red",
        "stage": "bold white reverse",
        "step": "bold white",
        "command": "dim white",
        "highlight": "bold magenta",
    }
)


class PipelineLogger:
    """Professional logger for pipeline execution logs using Rich.

    This class provides a set of methods to log messages with consistent styling
    and formatting. It is passed to the `run()` method of the pipeline.

    The actual output destination (stdout or widget stream) is handled by the
    `write_callback`.
    """

    def __init__(self, write_callback: Optional[Callable[[str], None]] = None):
        """Initialize the logger.

        Args:
            write_callback: Function to call for writing log output. If None,
                writes to sys.stdout.
        """
        self.callback = write_callback
        # Initialize rich console with the theme and forcing ANSI for widget compatibility
        self.console = Console(
            theme=PIPELINE_THEME,
            force_terminal=True,
            force_interactive=False,
            color_system="standard",  # Standard 8-color for best compatibility
            width=100,
            file=self,  # We act as the file to capture output
        )

    def write(self, text: str):
        """Standard write method so Rich can use this class as a file."""
        if self.callback:
            self.callback(text)
        else:
            sys.stdout.write(text)

    def flush(self):
        """Flush method for file-like interface."""
        pass

    def stage(self, name: str):
        """Log a major pipeline stage header.

        Displays the stage name in a prominent, reversed style block.
        Use this to mark significant phases of execution (e.g., "PREPROCESSING", "ANALYSIS").

        Args:
            name: Name of the stage.

        Examples:

            logger.stage("Data Preprocessing")
        """
        self.console.print()
        self.console.print(f" {name.upper()} ", style="stage")
        self.console.print()

    def step(self, text: str):
        """Log a step within the current stage.

        Prefixes the message with a chevron (❯).

        Args:
            text: Step description.

        Examples:

            logger.step("Aligning sequences with standard parameters")
        """
        self.console.print(f"❯ [step]{text}[/step]")

    def info(self, text: str):
        """Log an informational message.

        Prefixes the message with an info icon (ℹ).

        Args:
            text: Info message.

        Examples:

            logger.info("Found 14 matching sequences")
        """
        self.console.print(f"ℹ [info]{text}[/info]")

    def success(self, text: str):
        """Log a success message.

        Prefixes the message with a checkmark (✓) and styles it green.

        Args:
            text: Success message.

        Examples:

            logger.success("Alignment completed successfully")
        """
        self.console.print(f"✓ [success]{text}[/success]")

    def warning(self, text: str):
        """Log a warning message.

        Prefixes the message with a warning icon (⚠) and styles it yellow.

        Args:
            text: Warning message.

        Examples:

            logger.warning("Low quality scores detected in 3 samples")
        """
        self.console.print(f"⚠ [warning]{text}[/warning]")

    def error(self, text: str):
        """Log an error message.

        Prefixes the message with an error icon (✘) and styles it red.

        Args:
            text: Error message.

        Examples:

            logger.error("Process failed with exit code 1")
        """
        self.console.print(f"✘ [error]{text}[/error]")

    def command(self, cmd: str):
        """Log a command being executed.

        Prefixes the command with a dollar sign ($) and styles it as code.

        Args:
            cmd: Command string.

        Examples:

            logger.command("bowtie2 -x index -U reads.fq")
        """
        self.console.print(f"  [command]$ {cmd}[/command]")

    def plain(self, text: str):
        """Log plain text without any symbols or special prefixes.

        Args:
            text: Text content.
        """
        self.console.print(text)

    def indent(self, text: str, level: int = 1):
        """Log text with indentation.

        Args:
            text: Text content.
            level: Indentation level (default 1).
        """
        prefix = "  " * level
        self.console.print(f"{prefix}{text}")
