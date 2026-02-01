"""Command execution utilities for pipeline steps."""

import os
import subprocess
import shlex
import codecs
from pathlib import Path
from typing import Callable, List, Optional, Union

from ..execution.logging import PipelineLogger


def run_command(
    command: Union[str, List[str]],
    logger: PipelineLogger,
    stop_check: Optional[Callable[[], bool]] = None,
    on_process_start: Optional[Callable[[subprocess.Popen], None]] = None,
    cwd: Optional[Union[str, Path]] = None,
    use_pixi: bool = True,
) -> int:
    """Run a shell command with live log streaming.

    Args:
        command: Command string or list of arguments.
        logger: PipelineLogger for output.
        stop_check: Optional callback; returns True to abort execution.
        on_process_start: Optional callback receiving Popen object (e.g., for termination).
        cwd: Working directory for the command.
        use_pixi: If True and a pixi.lock exists, wrap command with `pixi run --`.

    Returns:
        Exit code (0 = success, -1 = terminated by stop_check, 1+ = error).

    Example:
        >>> run_command("ls -la", logger)
        0
        >>> run_command(["grep", "-r", "TODO", "."], logger)
        0
    """
    # Apply pixi wrapper if requested and available
    if use_pixi and isinstance(command, str):
        from .environment import wrap_command_for_pixi

        command = wrap_command_for_pixi(command)
    elif use_pixi and isinstance(command, list):
        from .environment import find_lockfile, get_pixi_env_bin

        lockfile = find_lockfile()
        if lockfile and get_pixi_env_bin(lockfile):
            command = ["pixi", "run", "--"] + command

    if isinstance(command, list):
        # Convert list to string for display, but use list for execution
        cmd_str = " ".join(shlex.quote(str(arg)) for arg in command)
        cmd_args = command
        shell_mode = False
    else:
        cmd_str = command
        cmd_args = command
        shell_mode = True

    logger.command(cmd_str)

    # Environment setup for unbuffered output
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    try:
        process = subprocess.Popen(
            cmd_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=shell_mode,
            text=False,  # Read bytes to handle any encoding issues gracefully
            bufsize=0,  # Unbuffered
            env=env,
            cwd=cwd,
        )

        if on_process_start:
            on_process_start(process)

        decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")

        while True:
            # Check for stop request
            if stop_check and stop_check():
                process.terminate()
                logger.warning("Terminated by user.")
                return -1

            # Non-blocking read (or small chunk read)
            chunk = process.stdout.read(1024)
            if not chunk:
                if process.poll() is not None:
                    break
                continue

            decoded = decoder.decode(chunk, final=False)
            if decoded:
                logger.plain(
                    decoded.rstrip()
                )  # rstrip to avoid double newlines from logger

        return process.poll()

    except FileNotFoundError:
        logger.error(
            f"Command not found: {cmd_args[0] if isinstance(cmd_args, list) else cmd_args.split()[0]}"
        )
        return 127
    except Exception as e:
        logger.error(f"Failed to execute command: {e}")
        return 1
