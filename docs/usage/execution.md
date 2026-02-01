---
icon: lucide/play
---

# Execution & Logging

The `run()` method is the entry point for your pipeline's logic. Pydgey executes this method in a separate thread so that the User Interface remains responsive (e.g., stopping buttons still work, logs still stream) while your heavy computation runs.

## The Run Method

Your run method receives two arguments:

1.  `params` (dict): A dictionary of all the values entered by the user.
2.  `logger` (`PipelineLogger`): A specialized object for communicating with the widget.

```python
def run(self, params, logger):
    logger.stage("Initializing")
    
    # 1. Get Inputs
    input_file = params.get("input_file")
    
    # 2. Run Logic
    if not input_file:
        logger.error("No input file provided!")
        return False
        
    # 3. Report Success
    return True
    return True
```

## Google Drive Integration

When running in Google Colab, you often want to save results to Google Drive. Pydgey provides a helper to handle authentication and mounting.

```python
from pydgey.runtime import mount_google_drive

def run(self, params, logger):
    # Check if user requested Drive export (e.g. from Components.GoogleDriveOutput)
    if params.get("use_drive"):
        logger.info("Connecting to Google Drive...")
        
        # This triggers the Colab auth popup if needed
        if mount_google_drive(logger=logger):
            drive_path = params.get("drive_path")
            # ... copy your results to drive_path ...
            logger.success(f"Results saved to {drive_path}")
        else:
            logger.error("Could not mount Drive")
```

## The Logging API

The `logger` is your primary way to talk to the user. It supports rich text, emojis, and styling.

| Method | Description | Example |
| :--- | :--- | :--- |
| `logger.info(msg)` | Standard informational message. | `logger.info("Reading file...")` |
| `logger.success(msg)` | Green success message. | `logger.success("Analysis complete!")` |
| `logger.warning(msg)` | Yellow warning message. | `logger.warning("Low memory detected")` |
| `logger.error(msg)` | Red error message. | `logger.error("File not found")` |
| `logger.stage(name)` | **Important**. Sets the current distinct phase of the pipeline. Example: "Preprocessing", "Alignment". | `logger.stage("Alignment")` |
| `logger.step(msg)` | A bullet point or sub-step within a stage. | `logger.step("Indexing reference...")` |
| `logger.code_block(text)` | Renders text in a monospaced code box. Good for showing shell commands. | `logger.code_block("blastn -query ...")` |

## Running Subprocesses

Most bioinformatics pipelines achieve their work by calling command-line tools (BLAST, Samtools, etc.). Pydgey provides a helper method `self.run_command` that handles this for you:

1.  It streams the `stdout` and `stderr` of the tool directly to the widget logs in real-time.
2.  It checks for **User Cancellation** automatically.
3.  It captures the exit code.

```python
def run(self, params, logger):
    cmd = f"blastn -query {params['query']} -db nt -outfmt 6"
    
    # Run the command and stream output to logger
    exit_code = self.run_command(cmd, logger)
    
    if exit_code != 0:
        logger.error(f"BLAST failed with exit code {exit_code}")
        return False
        
    logger.success("BLAST finished")
    return True
```

**Note**: `run_command` requires the tool (e.g., `blastn`) to be installed in the environment. See [Dependencies](dependencies.md).

## Handling Cancellation

Users can click the **Stop** button at any time.

*   If you are using `self.run_command`, Pydgey automtically kills the subprocess and stops your pipeline.
*   If you are writing pure Python loops, you must check `self.is_stopped` periodically.

```python
for item in heavy_work_items:
    # Manual check
    if self.is_stopped:
        logger.warning("Stopping early...")
        return False
        
    process_item(item)
```

## Exception Handling

If your `run` method raises an unhandled exception, Pydgey will catch it, log the full traceback to the widget console, and mark the execution as Failed.
