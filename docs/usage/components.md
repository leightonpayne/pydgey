---
icon: lucide/cuboid
---

# Component Patterns

The `pydgey.components` module provides a set of pre-built UI patterns that are commonly used in pipeline interfaces. 

Instead of building every form from scratch using `Field.Text` or `Layout.Section`, you can use these high-level `Components` to quickly assemble standard interfaces for file uploads, output configuration, and performance tuning.

## File Handling components

### FileInput

A standard wrapper for selecting input files. It handles the `visible_when` logic usually required if you want to allow users to switch between "Demo Data" and "Upload File".

```python
Components.FileInput(
    name="reads", 
    label="FASTQ Reads", 
    accept=[".fastq", ".fq", ".fq.gz"],
    multiple=True
)
```

### PairedEndInput

Specialized component for submitting paired-end reads (R1 and R2). It groups two file inputs into a visually distinct card.

```python
Components.PairedEndInput(
    r1_name="forward_reads",
    r2_name="reverse_reads"
)
```

### OutputConfig

A standardized section for defining where results should go. It typically includes an "Output Prefix" text field and an "Output Directory" field.

```python
Components.OutputConfig(
    prefix_default="my_result",
    include_directory=True
)
    include_directory=True
)
```

### GoogleDriveOutput

A specialized card for Colab users. It provides a toggle to "Save to Google Drive" and a "Drive Folder" path field.

```python
Components.GoogleDriveOutput(
    default_path="/content/drive/MyDrive/results"
)
```

## Configuration & Settings

### PerformanceSettings

A pre-built section for configuring CPU and Memory limits.

```python
Components.PerformanceSettings(
    cpu_default=4,
    include_memory=True,  # Adds a generic "Memory (GB)" field
    memory_default=16
)
```

### ThresholdSettings

A card designed for numeric threshold parameters (e-values, scores, etc.).

```python
Components.ThresholdSettings([
    {"name": "evalue", "label": "E-value", "default": 1e-5},
    {"name": "min_len", "label": "Min Length", "default": 500, "type": "int"}
])
```

## Advanced Composition

### AdvancedSection

A collapsible section that is collapsed by default. This is perfect for hiding complex parameters that most users shouldn't touch.

```python
Components.AdvancedSection(
    title="Expert Parameters",
    children=[
        Field.Switch("verbose_mode", "Verbose Logging"),
        Field.Float("sensitivity", "Sensitivity", default=0.95)
    ]
)
```

### ConditionalField

Wraps any field to make it conditionally visible based on another field's value. This is a helper around the raw `visible_when` API.

```python
Components.ConditionalField(
    field=Field.Text("api_key", "API Key"),
    depends_on="use_cloud_service",
    value=True
)
```
