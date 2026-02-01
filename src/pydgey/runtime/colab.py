import sys
import os
import subprocess
import threading
from pathlib import Path
from typing import Optional

from ..execution import PipelineLogger


def check_colab() -> bool:
    """Check if the code is running inside Google Colab.

    This utility inspects `sys.modules` to determine if the environment
    is Google Colab.

    Returns:
        bool: True if running in Colab, False otherwise.
    """
    return "google.colab" in sys.modules


def setup_colab() -> None:
    """Prepare the Google Colab environment for pipeline execution.

    This function performs necessary setup steps when running in Colab:
    1.  Checks if Pixi is installed, and installs it if missing.
    2.  Runs `pixi install` to set up dependencies defined in `pixi.lock`.
    3.  Updates the `PATH` environment variable to include Pixi-installed binaries.

    It is safe to call this function unconditionally; it will exit early
    if not running in Colab.
    """
    if not check_colab():
        return

    logger = PipelineLogger()

    if subprocess.call("which pixi", shell=True) != 0:
        logger.info("Installing Pixi...")
        subprocess.run(
            "curl -fsSL https://pixi.sh/install.sh | bash",
            shell=True,
            check=True,
        )
        os.environ["PATH"] += os.pathsep + str(Path.home() / ".pixi/bin")

    logger.info("Installing tools from pixi.lock...")
    subprocess.run("pixi install", shell=True, check=True)

    pixi_env_bin = Path.cwd() / ".pixi/envs/default/bin"
    if pixi_env_bin.exists():
        os.environ["PATH"] = str(pixi_env_bin) + os.pathsep + os.environ["PATH"]

    logger.success("Setup complete")


def keep_alive_thread(interval_seconds: int = 30) -> threading.Thread:
    """Start a background thread to prevent Colab usage timeouts.

    Google Colab runtimes may disconnect if there is no interactivity for a
    certain period. This helper starts a daemon thread that wakes up periodically,
    helping to keep the session active during long-running pipelines.

    Args:
        interval_seconds: Time in seconds between heartbeats.

    Returns:
        threading.Thread: The background thread instance.
    """
    import time

    def _heartbeat() -> None:
        while True:
            time.sleep(interval_seconds)

    t = threading.Thread(target=_heartbeat, daemon=True)
    t.start()
    return t


def mount_google_drive(
    mount_point: str = "/content/drive",
    logger: Optional[PipelineLogger] = None,
) -> bool:
    """Mount Google Drive in Colab environment.

    This function attempts to mount Google Drive at the specified mount point.
    It is a no-op if not running in Google Colab.

    Args:
        mount_point: Directory to mount Drive to.
        logger: Optional logger to record status.

    Returns:
        bool: True if mounted successfully or not in Colab, False on failure.
    """
    if not check_colab():
        return True

    if logger:
        logger.info("Mounting Google Drive...")

    try:
        from google.colab import drive  # type: ignore

        if not os.path.exists(mount_point):
            drive.mount(mount_point)
            if logger:
                logger.success(f"Drive mounted at {mount_point}")
        else:
            if logger:
                logger.info(f"Drive already mounted at {mount_point}")
        return True
    except Exception as e:
        if logger:
            logger.error(f"Failed to mount Drive: {e}")
        return False
