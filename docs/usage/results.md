---
icon: lucide/package-check
---
# Results Handling

Managing final outputs effectively is crucial for a good user experience. Pydgey provides the `ResultBundle` class to help you organize output files and package them into a downloadable ZIP archive for the user.

## The Standard Workflow

The recommended pattern is to perform your analysis, and then at the end of the `run()` method, bundle the results.

```python
from pydgey import Pipeline, ResultBundle

class MyPipeline(Pipeline):
    def run(self, params, logger):
        # ... perform logic producing files in ./output/ ...
        
        # 1. Create a bundle (manifest)
        bundle = ResultBundle(
            name="analysis_results", 
            base_dir="./output"
        )
        
        # 2. Add specific critical files
        bundle.add_file("summary.txt", description="Summary metrics")
        bundle.add_file("results.csv", description="Result Table")
        
        # 3. Add entire directories of plots/logs
        bundle.add_directory("plots", description="Visualizations")
        
        # 4. Package into a ZIP file
        zip_path = bundle.create_zip()
        
        if zip_path:
            logger.success(f"Results packaged: {zip_path.name}")
        else:
            logger.warning("No results found to package.")
            
        return True
```

## The ResultBundle Class

`ResultBundle` acts as a smart manifest for your outputs. It doesn't move files immediately; it records what you want to include.

### Initialization

```python
bundle = ResultBundle(
    name="my_run",         # Used for the default zip filename (my_run_results.zip)
    base_dir="./output"    # Base path for resolving relative file paths
)
```

### Adding Content

You can add individual files or entire directory trees.

| Method | Description |
| :--- | :--- |
| `add_file(path, description="")` | Adds a single file. Raises warning if not found. |
| `add_directory(path, pattern="*", description="")` | Adds all files in a folder matching the glob pattern. |

```python
# specific file
bundle.add_file("final_report.html", description="Interactive Report")

# all PNGs in the figures folder
bundle.add_directory("figures", pattern="*.png", description="Plots")
```

## Creating the Archive

The `create_zip()` method performs the work of compressing the bundled files into a single archive.

```python
# Creates ./output/my_run_results.zip
zip_path = bundle.create_zip()
```

The resulting ZIP file:
1.  Is placed in the `base_dir` (by default).
2.  Preserves the directory structure of added files relative to `base_dir`.

## Widget Integration

When you create a ZIP file named `{name}_results.zip`, the **Pydgey Widget** automatically detects it and enables the **Download Results** button in the frontend.

This provides a seamless "Click to Run" → "Click to Download" experience for your users.

!!! tip
    If you have multiple output files, `ResultBundle` is strongly recommended over asking users to manually download files from the file browser.
