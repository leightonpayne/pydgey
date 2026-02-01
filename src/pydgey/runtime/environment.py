"""Pixi environment management for reproducible dependencies.

This module provides utilities for detecting, installing, and activating
Pixi-managed environments. It enables pipelines to ship with a `pixi.lock`
file that guarantees reproducible tool installations across environments.

Example:
    ```python
    from pydgey import check_environment, setup_environment, PipelineLogger

    # Check current state
    env = check_environment()
    print(f"Lockfile: {env.lockfile_path}")
    print(f"Ready: {env.is_ready}")

    # Auto-setup if needed
    logger = PipelineLogger()
    success, env = setup_environment(logger)
    ```
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple
from dataclasses import dataclass

from ..execution.logging import PipelineLogger


@dataclass
class PixiEnvironment:
    """Represents the state of a Pixi environment.

    Attributes:
        lockfile_path: Path to the detected pixi.lock file.
        env_bin_path: Path to the environment's bin directory.
        is_ready: True if the environment is fully set up.
        pixi_installed: True if the `pixi` command is available.

    Example:
        ```python
        env = check_environment()
        if env.is_ready:
            print(f"Tools available at: {env.env_bin_path}")
        ```
    """

    lockfile_path: Optional[Path] = None
    env_bin_path: Optional[Path] = None
    is_ready: bool = False
    pixi_installed: bool = False


def check_colab() -> bool:
    """Check if running in Google Colab.

    Returns:
        True if running in Colab, False otherwise.

    Example:
        ```python
        if check_colab():
            print("Running in Google Colab")
        ```
    """
    return "google.colab" in sys.modules


def find_lockfile(
    start_dir: Optional[Path] = None, max_depth: int = 3
) -> Optional[Path]:
    """Search for a pixi.lock file starting from a directory.

    Walks up the directory tree looking for `pixi.lock`.

    Args:
        start_dir: Directory to start searching from. Defaults to cwd.
        max_depth: Maximum number of parent directories to check.

    Returns:
        Path to pixi.lock if found, None otherwise.

    Example:
        ```python
        lockfile = find_lockfile()
        if lockfile:
            print(f"Found lockfile at: {lockfile}")
        ```
    """
    if start_dir is None:
        start_dir = Path.cwd()

    current = start_dir.resolve()

    for _ in range(max_depth + 1):
        lockfile = current / "pixi.lock"
        if lockfile.exists():
            return lockfile

        parent = current.parent
        if parent == current:  # Reached root
            break
        current = parent

    return None


def is_pixi_installed() -> bool:
    """Check if Pixi is installed and accessible.

    Returns:
        True if `pixi` command is available.

    Example:
        ```python
        if is_pixi_installed():
            print("Pixi is ready")
        else:
            print("Please install Pixi: https://pixi.sh")
        ```
    """
    try:
        result = subprocess.run(
            ["pixi", "--version"], capture_output=True, text=True, timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def check_tool(command: str) -> Tuple[bool, Optional[str]]:
    """Check if a command-line tool is available.

    This is a simple utility for verifying tool availability,
    useful for debugging or pre-flight checks.

    Args:
        command: The command to check (e.g., "hmmsearch").

    Returns:
        Tuple of (found: bool, version: Optional[str]).

    Example:
        ```python
        found, version = check_tool("blastn")
        if found:
            print(f"BLAST version: {version}")
        else:
            print("BLAST not installed")
        ```
    """
    import shutil

    path = shutil.which(command)
    if not path:
        return False, None

    try:
        result = subprocess.run(
            [command, "--version"], capture_output=True, text=True, timeout=5
        )
        version = (result.stdout or result.stderr).strip().split("\n")[0]
        return True, version
    except Exception:
        return True, None


def get_pixi_env_bin(lockfile_path: Path) -> Optional[Path]:
    """Get the path to the Pixi environment's bin directory.

    Args:
        lockfile_path: Path to the pixi.lock file.

    Returns:
        Path to .pixi/envs/default/bin if it exists, None otherwise.

    Example:
        ```python
        lockfile = find_lockfile()
        if lockfile:
            bin_path = get_pixi_env_bin(lockfile)
            if bin_path:
                print(f"Tools at: {bin_path}")
        ```
    """
    project_root = lockfile_path.parent
    env_bin = project_root / ".pixi" / "envs" / "default" / "bin"
    return env_bin if env_bin.exists() else None


def check_environment(lockfile_path: Optional[Path] = None) -> PixiEnvironment:
    """Assess the current Pixi environment state.

    Args:
        lockfile_path: Optional explicit path to pixi.lock.

    Returns:
        PixiEnvironment with detection results.

    Example:
        ```python
        env = check_environment()
        if not env.lockfile_path:
            print("No pixi.lock found")
        elif not env.is_ready:
            print("Environment needs setup")
        else:
            print("Environment ready!")
        ```
    """
    env = PixiEnvironment()

    # Find lockfile
    env.lockfile_path = lockfile_path or find_lockfile()
    if not env.lockfile_path:
        return env

    # Check if Pixi is installed
    env.pixi_installed = is_pixi_installed()

    # Check if environment is ready
    env.env_bin_path = get_pixi_env_bin(env.lockfile_path)
    env.is_ready = env.env_bin_path is not None

    return env


def install_pixi(logger: PipelineLogger) -> bool:
    """Install Pixi using the official installer.

    Downloads and runs the Pixi installer script. Only intended for
    use in ephemeral environments like Google Colab.

    Args:
        logger: Logger for streaming output.

    Returns:
        True if installation succeeded.

    Example:
        ```python
        logger = PipelineLogger()
        if install_pixi(logger):
            print("Pixi installed!")
        ```
    """
    logger.stage("Installing Pixi")
    logger.info("Downloading Pixi installer...")

    try:
        # Run the Pixi installer
        process = subprocess.Popen(
            "curl -fsSL https://pixi.sh/install.sh | bash",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        for line in process.stdout:
            logger.plain(line.rstrip())

        process.wait()

        if process.returncode != 0:
            logger.error(f"Pixi installation failed (exit code {process.returncode})")
            return False

        # Add Pixi to PATH for this session
        pixi_bin = Path.home() / ".pixi" / "bin"
        if pixi_bin.exists():
            os.environ["PATH"] = str(pixi_bin) + os.pathsep + os.environ["PATH"]
            logger.success("Pixi installed successfully")
            return True
        else:
            logger.error("Pixi binary not found after installation")
            return False

    except Exception as e:
        logger.error(f"Failed to install Pixi: {e}")
        return False


def run_pixi_install(lockfile_path: Path, logger: PipelineLogger) -> bool:
    """Run `pixi install` in the project directory.

    Args:
        lockfile_path: Path to pixi.lock file.
        logger: Logger for streaming output.

    Returns:
        True if installation succeeded.

    Example:
        ```python
        lockfile = find_lockfile()
        logger = PipelineLogger()
        if run_pixi_install(lockfile, logger):
            print("Dependencies installed!")
        ```
    """
    project_root = lockfile_path.parent

    logger.stage("Installing Dependencies")
    logger.info(f"Running pixi install in {project_root}")

    try:
        process = subprocess.Popen(
            ["pixi", "install"],
            cwd=project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        for line in process.stdout:
            logger.plain(line.rstrip())

        process.wait()

        if process.returncode != 0:
            logger.error(f"pixi install failed (exit code {process.returncode})")
            return False

        logger.success("Dependencies installed successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to run pixi install: {e}")
        return False


def setup_environment(
    logger: PipelineLogger, lockfile_path: Optional[Path] = None
) -> Tuple[bool, PixiEnvironment]:
    """Set up the Pixi environment if needed.

    This is the main entry point for environment setup. It:

    1. Detects if a pixi.lock exists
    2. Installs Pixi if needed (Colab only)
    3. Runs `pixi install` if environment not ready

    On local machines, it warns but does not auto-install.

    Args:
        logger: Logger for streaming output.
        lockfile_path: Optional explicit lockfile path.

    Returns:
        Tuple of (success: bool, env: PixiEnvironment).

    Example:
        ```python
        from pydgey import setup_environment, PipelineLogger

        logger = PipelineLogger()
        success, env = setup_environment(logger)

        if success and env.is_ready:
            print("Ready to run pipeline!")
        elif not success:
            print("Environment setup failed")
        ```
    """
    env = check_environment(lockfile_path)

    # No lockfile = no dependencies to manage
    if not env.lockfile_path:
        return (True, env)

    # Environment already ready
    if env.is_ready:
        logger.info("Environment already set up")
        return (True, env)

    # Not in Colab = warn and continue (local user should run pixi shell)
    if not check_colab():
        logger.warning(
            "Pixi environment not activated. "
            "For best results, run `pixi shell` in your terminal first, "
            "or use `pixi run jupyter lab`."
        )
        return (True, env)

    # Colab: auto-setup
    logger.stage("Setting Up Environment")

    # Install Pixi if needed
    if not env.pixi_installed:
        if not install_pixi(logger):
            return (False, env)
        env.pixi_installed = True

    # Run pixi install
    if not run_pixi_install(env.lockfile_path, logger):
        return (False, env)

    # Update environment state
    env.env_bin_path = get_pixi_env_bin(env.lockfile_path)
    env.is_ready = env.env_bin_path is not None

    if env.is_ready:
        logger.success("Environment ready")
    else:
        logger.error("Environment setup completed but bin directory not found")

    return (env.is_ready, env)


def wrap_command_for_pixi(command: str, lockfile_path: Optional[Path] = None) -> str:
    """Wrap a command to run inside the Pixi environment.

    This function is used internally by `run_command` to ensure
    commands execute within the Pixi-managed environment.

    Args:
        command: The command to wrap.
        lockfile_path: Path to pixi.lock (to find project root).

    Returns:
        Command prefixed with `pixi run --` or original if no lockfile.

    Example:
        ```python
        cmd = wrap_command_for_pixi("hmmsearch --help")
        # Returns: "pixi run -- hmmsearch --help"
        ```
    """
    if lockfile_path is None:
        lockfile_path = find_lockfile()

    if lockfile_path is None:
        return command

    # Check if environment exists
    env_bin = get_pixi_env_bin(lockfile_path)
    if env_bin is None:
        return command

    return f"pixi run -- {command}"
