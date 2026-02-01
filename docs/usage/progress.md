---
icon: lucide/timer
---
# Progress Tracking

Long-running pipelines need to show more than just scrolling logs. Pydgey provides a `Progress` utility class that allows you to define flexible, structured milestones that visualize the execution status in real-time.

## Basic Usage

You define a list of high-level steps, and then use the `progress` object to mark them as running or complete.

```python
from pydgey import Progress
import time

def run(self, params, logger):
    # 1. Initialize tracker with known steps
    progress = Progress([
        "Validation",
        "Preprocessing",
        "Analysis",
        "Report Generation"
    ])

    # 2. Use the context manager for each step
    with progress.step("Validation"):
        check_inputs(params)
        time.sleep(1)

    with progress.step("Preprocessing") as step:
        step.message = "Cleaning sequences..." # Optional sub-status
        clean_data()

    return True
```

## The Context Manager

The `with progress.step("Name"):` block is the recommended pattern. It handles all state transitions for you:

1.  **Enter**: Sets step to **Running**, records start time.
2.  **Exit (Success)**: Sets step to **Completed**, records end time.
3.  **Exit (Exception)**: Sets step to **Failed**, logs error.

```python
try:
    with progress.step("Critical Alignment"):
        run_alignment_tool()
except Exception:
    # The UI will show "Critical Alignment" as red/failed.
    logger.error("Alignment crashed!")
    return False
```

## Dynamic Steps

You don't have to know every step in advance. You can add them dynamically as your logic unfolds.

```python
progress = Progress() # Empty start

# Step 1
with progress.step("Setup"):
    prepare_env()

# Step 2 (dynamically added)
if params.get("do_extra_work"):
    with progress.step("Extra Analysis"):
        run_extra()
```

## Creating Nested Progress

For very complex tools, you might want to report percentage progress within a single large step.

Currently, Pydgey's `Progress` component focuses on **Milestone Tracking** (Step 1, Step 2, Step 3) rather than granular percentages (45%).

!!! tip
    For granular feedback within a loop, stick to `logger.info()`:
    ```python
    for i, item in enumerate(items):
        logger.info(f"Processing {i}/{total}...")
    ```

## Skipping Steps

If a step is conditional, you can explicitly mark it as skipped so the user knows it was intentionally bypassed.

```python
if not params.get("generate_pdf"):
    progress.skip("PDF Report", "Disabled in settings")
else:
    with progress.step("PDF Report"):
        make_pdf()
```
