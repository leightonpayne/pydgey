"""Pre-built component patterns for common pipeline UIs.

This module provides factory functions that create common UI patterns
combining multiple layout elements and fields.
"""

from typing import Any, Dict, List, Optional, Tuple

from .elements import Layout, UIElement
from .fields import Field
from .validators import Validators


class Components:
    """Factory for common UI component patterns."""

    @staticmethod
    def FileInput(
        name: str = "input_file",
        label: str = "Input File",
        accept: Optional[List[str]] = None,
        multiple: bool = False,
        description: str = "",
        required: bool = True,
    ) -> UIElement:
        """Create a file input with optional extension validation.

        Args:
            name: Parameter name.
            label: Display label.
            accept: List of accepted file extensions.
            multiple: Allow multiple files.
            description: Help text.
            required: If True, adds required validator.

        Examples:
            ```python
            Components.FileInput(
                "reads", "FASTQ Reads",
                accept=[".fastq", ".fq", ".fq.gz"],
                multiple=True
            )
            ```
        """
        validators = []
        if required:
            validators.append(Validators.required())
        if accept:
            validators.append(Validators.file_extension(accept))

        return Field.File(
            name=name,
            label=label,
            accept=accept,
            multiple=multiple,
            description=description,
            validators=validators if validators else None,
        )

    @staticmethod
    def OutputConfig(
        prefix_name: str = "output_prefix",
        prefix_label: str = "Output Prefix",
        prefix_default: str = "output",
        include_directory: bool = False,
        directory_name: str = "output_dir",
        directory_default: str = "./results",
    ) -> UIElement:
        """Create an output configuration card.

        Args:
            prefix_name: Parameter name for output prefix.
            prefix_label: Label for prefix field.
            prefix_default: Default prefix value.
            include_directory: Include output directory field.
            directory_name: Parameter name for directory.
            directory_default: Default directory value.

        Examples:
            ```python
            Components.OutputConfig(
                prefix_default="hmmsearch_result",
                include_directory=True
            )
            ```
        """
        children = [
            Field.Text(
                prefix_name,
                prefix_label,
                default=prefix_default,
                description="Prefix for generated output files",
            ),
        ]

        if include_directory:
            children.append(
                Field.Text(
                    directory_name,
                    "Output Directory",
                    default=directory_default,
                    description="Directory for output files",
                )
            )

        return Layout.Card("Output Settings", children)

    @staticmethod
    def PerformanceSettings(
        cpu_name: str = "cpu",
        cpu_default: int = 4,
        cpu_max: Optional[int] = None,
        include_memory: bool = False,
        memory_name: str = "memory_gb",
        memory_default: int = 8,
    ) -> UIElement:
        """Create a performance settings card.

        Args:
            cpu_name: Parameter name for CPU cores.
            cpu_default: Default CPU count.
            cpu_max: Maximum CPU count (None = no limit).
            include_memory: Include memory setting.
            memory_name: Parameter name for memory.
            memory_default: Default memory in GB.

        Examples:
            ```python
            Components.PerformanceSettings(cpu_default=8, include_memory=True)
            ```
        """
        children = [
            Field.Int(
                cpu_name,
                "CPU Cores",
                default=cpu_default,
                min=1,
                max=cpu_max,
                description="Number of CPU cores to use",
            ),
        ]

        if include_memory:
            children.append(
                Field.Int(
                    memory_name,
                    "Memory (GB)",
                    default=memory_default,
                    min=1,
                    description="Memory limit in gigabytes",
                )
            )

        return Layout.Card("Performance", children)

    @staticmethod
    def ThresholdSettings(
        thresholds: List[Dict[str, Any]],
        title: str = "Thresholds",
    ) -> UIElement:
        """Create a thresholds configuration card.

        Args:
            thresholds: List of threshold definitions, each with:
                - name: Parameter name
                - label: Display label
                - default: Default value
                - description: Help text (optional)
                - type: "int" or "float" (default: "float")
            title: Card title.

        Examples:
            ```python
            Components.ThresholdSettings([
                {"name": "evalue", "label": "E-value", "default": 1e-5},
                {"name": "score", "label": "Min Score", "default": 50, "type": "int"},
            ])
            ```
        """
        children = []

        for t in thresholds:
            field_type = t.get("type", "float")
            if field_type == "int":
                children.append(
                    Field.Int(
                        t["name"],
                        t["label"],
                        default=t.get("default", 0),
                        description=t.get("description", ""),
                    )
                )
            else:
                children.append(
                    Field.Float(
                        t["name"],
                        t["label"],
                        default=t.get("default", 0.0),
                        description=t.get("description", ""),
                    )
                )

        return Layout.Card(title, children)

    @staticmethod
    def AdvancedSection(
        children: List[UIElement],
        title: str = "Advanced Options",
        collapsed: bool = True,
        visible_when: Optional[Tuple[str, str, Any]] = None,
    ) -> UIElement:
        """Create a collapsible advanced options section.

        Args:
            children: Child elements.
            title: Section title.
            collapsed: Start collapsed.
            visible_when: Conditional visibility.

        Examples:
            ```python
            Components.AdvancedSection([
                Field.Switch("debug", "Debug Mode"),
                Field.Int("seed", "Random Seed", default=42),
            ])
            ```
        """
        return Layout.Section(
            title,
            children,
            collapsed=collapsed,
            visible_when=visible_when,
        )

    @staticmethod
    def ConditionalField(
        field: UIElement,
        depends_on: str,
        operator: str = "==",
        value: Any = True,
    ) -> UIElement:
        """Wrap a field with conditional visibility.

        Args:
            field: The field to conditionally show.
            depends_on: Name of the field this depends on.
            operator: Comparison operator ("==", "!=", ">", "<", ">=", "<=").
            value: Value to compare against.

        Examples:
            ```python
            Components.ConditionalField(
                Field.Text("custom_path", "Custom Path"),
                depends_on="use_custom",
                value=True
            )
            ```
        """
        # Clone the field with visible_when
        return UIElement(
            type=field.type,
            props=field.props,
            children=field.children,
            visible_when=(depends_on, operator, value),
        )

    @staticmethod
    def ToolInstallAction(
        action_name: str = "install_tools",
        button_label: str = "Install Dependencies",
    ) -> Dict[str, Any]:
        """Create an action config for tool installation.

        This returns a config dict to add to PipelineConfig.

        Args:
            action_name: Action identifier.
            button_label: Button text in UI.

        Examples:
            ```python
            config = PipelineConfig(
                actions=[Components.ToolInstallAction()]
            )
            ```
        """
        return {
            "name": action_name,
            "label": button_label,
            "icon": "download",
            "variant": "secondary",
        }

    # ===== Bioinformatics Components =====

    @staticmethod
    def FastaInput(
        name: str = "fasta_file",
        label: str = "FASTA/FASTQ File",
        accept: Optional[List[str]] = None,
        multiple: bool = False,
        description: str = "",
        required: bool = True,
    ) -> UIElement:
        """Create a file input optimized for FASTA/FASTQ files.

        Automatically configures accepted extensions for common sequence formats
        including compressed variants.

        Args:
            name: Parameter name.
            label: Display label.
            accept: Override accepted extensions. Defaults to common sequence formats.
            multiple: Allow multiple files.
            description: Help text.
            required: If True, adds required validator.

        Examples:
            ```python
            Components.FastaInput("reads", "Sequence Reads", multiple=True)
            ```
        """
        if accept is None:
            accept = [
                ".fasta",
                ".fa",
                ".fna",
                ".ffn",
                ".faa",  # FASTA variants
                ".fastq",
                ".fq",  # FASTQ variants
                ".fasta.gz",
                ".fa.gz",
                ".fna.gz",  # Compressed FASTA
                ".fastq.gz",
                ".fq.gz",  # Compressed FASTQ
            ]

        validators = []
        if required:
            validators.append(Validators.required("Sequence file is required"))
        validators.append(Validators.file_extension(accept))

        return Field.File(
            name=name,
            label=label,
            accept=accept,
            multiple=multiple,
            description=description or "Accepts FASTA/FASTQ files (gzipped supported)",
            validators=validators if validators else None,
        )

    @staticmethod
    def PairedEndInput(
        r1_name: str = "reads_r1",
        r2_name: str = "reads_r2",
        r1_label: str = "Forward Reads (R1)",
        r2_label: str = "Reverse Reads (R2)",
        title: str = "Paired-End Reads",
        description: str = "",
    ) -> UIElement:
        """Create a paired-end reads input card with R1/R2 file uploads.

        Configures both inputs for common FASTQ extensions.

        Args:
            r1_name: Parameter name for forward reads.
            r2_name: Parameter name for reverse reads.
            r1_label: Label for R1 input.
            r2_label: Label for R2 input.
            title: Card title.
            description: Card description.

        Examples:
            ```python
            Components.PairedEndInput(
                r1_name="forward",
                r2_name="reverse",
                title="Illumina Reads"
            )
            ```
        """
        fastq_extensions = [".fastq", ".fq", ".fastq.gz", ".fq.gz"]

        children = []

        if description:
            children.append(Layout.Text(description, class_name="text-muted"))

        children.extend(
            [
                Layout.Row(
                    [
                        Field.File(
                            name=r1_name,
                            label=r1_label,
                            accept=fastq_extensions,
                            description="Forward reads file",
                            validators=[
                                Validators.required("Forward reads required"),
                                Validators.file_extension(fastq_extensions),
                            ],
                        ),
                        Field.File(
                            name=r2_name,
                            label=r2_label,
                            accept=fastq_extensions,
                            description="Reverse reads file",
                            validators=[
                                Validators.required("Reverse reads required"),
                                Validators.file_extension(fastq_extensions),
                            ],
                        ),
                    ]
                ),
            ]
        )

        return Layout.Card(title, children)

    @staticmethod
    def InputPreview(
        file_field: str,
        preview_name: str = "input_preview",
        title: str = "Input Preview",
        max_sequences: int = 5,
    ) -> UIElement:
        """Create a preview section that shows sequence file statistics.

        This creates a display-only section. The actual preview content
        must be populated by the pipeline's run method using the logger.

        Args:
            file_field: Name of the file input field to preview.
            preview_name: Internal name for the preview element.
            title: Section title.
            max_sequences: Suggested number of sequences to show.

        Examples:
            ```python
            Components.InputPreview("fasta_file", title="Sequence Preview")
            ```

        Note:
            To populate the preview in your pipeline:
            ```python
            def run(self, params, logger):
                file_path = params.get("fasta_file")
                if file_path:
                    # Parse and log first N sequences
                    logger.info(f"File: {file_path}")
                    logger.info(f"Sequences: {count}")
            ```
        """
        return Layout.Section(
            title,
            [
                Layout.Html(
                    f"<div id='{preview_name}' class='text-xs text-slate-500'>"
                    f"<p>Upload a file in <code>{file_field}</code> to see preview.</p>"
                    f"<p class='text-[10px] text-slate-400 mt-1'>"
                    f"Shows first {max_sequences} sequences after upload.</p>"
                    "</div>"
                ),
            ],
            collapsed=False,
            visible_when=(file_field, "!=", None),
        )

    @staticmethod
    def GoogleDriveOutput(
        mount_drive_name: str = "use_drive",
        drive_path_name: str = "drive_path",
        default_path: str = "/content/drive/MyDrive/results",
        title: str = "Export",
    ) -> UIElement:
        """Create a Google Drive export configuration card.

        Includes a toggle to enable Drive export and a path field.

        Args:
            mount_drive_name: Parameter name for enabling Drive.
            drive_path_name: Parameter name for Drive path.
            default_path: Default export directory in Drive.
            title: Card title.

        Examples:
            ```python
            Components.GoogleDriveOutput()
            ```
        """
        children = [
            Field.Switch(mount_drive_name, "Save to Google Drive", default=False),
            Components.ConditionalField(
                Field.Text(
                    drive_path_name,
                    "Drive Folder",
                    default=default_path,
                    description="Folder in Google Drive to save results",
                ),
                depends_on=mount_drive_name,
            ),
        ]
        return Layout.Card(title, children)


# Convenience aliases
FileInput = Components.FileInput
OutputConfig = Components.OutputConfig
PerformanceSettings = Components.PerformanceSettings
ThresholdSettings = Components.ThresholdSettings
AdvancedSection = Components.AdvancedSection
ConditionalField = Components.ConditionalField
FastaInput = Components.FastaInput
PairedEndInput = Components.PairedEndInput
InputPreview = Components.InputPreview
GoogleDriveOutput = Components.GoogleDriveOutput
