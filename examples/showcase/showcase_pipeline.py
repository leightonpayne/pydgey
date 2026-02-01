"""
Color Mixer Studio - Pydgey Feature Showcase

This pipeline demonstrates all Pydgey features through a color mixing theme.
"""

import time
from pathlib import Path
from pydgey import (
    Pipeline,
    PipelineConfig,
    Layout,
    Field,
    Components,
    PipelineLogger,
    Progress,
    ResultBundle,
    action,
    Validators,
)


class ColorMixerPipeline(Pipeline):
    """
    A Pydgey feature showcase through color mixing.
    """

    def __init__(self):
        config = PipelineConfig(
            name="color_mixer",
            title="🎨 Color Mixer Studio",
            subtitle="A Pydgey feature showcase through color mixing",
            actions=[
                {
                    "name": "color_theory",
                    "label": "Color Theory Guide",
                    "icon": "info",
                    "variant": "secondary",
                }
            ],
        )
        super().__init__(config)
        self.progress = Progress(
            [
                "Analyzing Colors",
                "Mixing Pigments",
                "Applying Effects",
                "Generating Output",
            ]
        )

    def define_layout(self):
        return Layout.Page(
            [
                Layout.Tabs(
                    [
                        Layout.Tab(
                            "Color Mixer",
                            [
                                Layout.Card(
                                    "Primary Color Selection",
                                    [
                                        Field.MultiSelect(
                                            "colors",
                                            "Colors to Mix",
                                            options=["🔴 Red", "🔵 Blue", "🟡 Yellow"],
                                            default=["🔴 Red", "🔵 Blue"],
                                            description="`Field.MultiSelect` demo",
                                        ),
                                    ],
                                ),
                                Layout.Section(
                                    "Mix Settings",
                                    [
                                        Layout.Row(
                                            [
                                                Field.Select(
                                                    "intensity",
                                                    "Intensity",
                                                    options=[
                                                        "Light",
                                                        "Medium",
                                                        "Vibrant",
                                                    ],
                                                    default="Medium",
                                                    description="`Field.Select`",
                                                ),
                                                Field.Int(
                                                    "saturation",
                                                    "Saturation %",
                                                    default=75,
                                                    min=0,
                                                    max=100,
                                                    description="`Field.Int` with `min` and `max`",
                                                ),
                                                Field.Float(
                                                    "opacity",
                                                    "Opacity",
                                                    default=1.0,
                                                    min=0.0,
                                                    max=1.0,
                                                    step=0.05,
                                                    description="`Field.Float` with `min`, `max` and `step`",
                                                ),
                                            ]
                                        ),
                                        Layout.Row(
                                            [
                                                Field.Switch(
                                                    "add_white",
                                                    "Add White (Tint)",
                                                    default=False,
                                                ),
                                                Field.Switch(
                                                    "add_black",
                                                    "Add Black (Shade)",
                                                    default=False,
                                                ),
                                            ]
                                        ),
                                    ],
                                    collapsed=False,
                                ),
                            ],
                        ),
                        Layout.Tab(
                            "I/O",
                            [
                                Layout.Row(
                                    [
                                        Layout.Card(
                                            "Text Inputs",
                                            [
                                                Field.Text(
                                                    "project_name",
                                                    "Project Name",
                                                    default="my_color_project",
                                                    placeholder="Enter project name...",
                                                    description="`Field.Text` with `placeholder`",
                                                    validators=[
                                                        Validators.required(
                                                            "Project name is required"
                                                        ),
                                                        Validators.min_length(
                                                            3, "At least 3 characters"
                                                        ),
                                                    ],
                                                ),
                                                Field.TextArea(
                                                    "notes",
                                                    "Color Notes",
                                                    default="Add any notes about your color choices here.",
                                                    rows=3,
                                                    description="`Field.TextArea` with `rows`",
                                                ),
                                            ],
                                        ),
                                        Layout.Card(
                                            "File Input",
                                            [
                                                Components.FileInput(
                                                    "palette_file",
                                                    "Import Palette",
                                                    accept=[".json", ".txt", ".csv"],
                                                    required=False,
                                                    description="`Components.FileInput` with `accept` and `required`",
                                                ),
                                                Layout.Text(
                                                    "Optional: Import a color palette file",
                                                    class_name="text-muted",
                                                ),
                                            ],
                                        ),
                                        Layout.Row(
                                            [
                                                Components.OutputConfig(
                                                    prefix_default="color_mix",
                                                    include_directory=True,
                                                ),
                                            ]
                                        ),
                                    ]
                                ),
                            ],
                        ),
                        Layout.Tab(
                            "Config",
                            [
                                Components.PerformanceSettings(
                                    cpu_default=4,
                                    cpu_max=16,
                                    include_memory=True,
                                    memory_default=8,
                                ),
                                Components.AdvancedSection(
                                    [
                                        Field.Switch("debug_mode", "Debug Mode"),
                                        Field.Int(
                                            "random_seed", "Random Seed", default=42
                                        ),
                                        Field.Text(
                                            "api_key", "API Key", placeholder="Optional"
                                        ),
                                    ],
                                    title="Advanced Options",
                                ),
                            ],
                        ),
                        Layout.Tab(
                            "Conditional",
                            [
                                Layout.Card(
                                    "Conditional Visibility Demo",
                                    [
                                        Layout.Html(
                                            "<p style='color: #64748b; margin-bottom: 1rem;'>"
                                            "Toggle the switch to show/hide conditional fields. "
                                            "This demonstrates <code>visible_when</code> logic."
                                            "</p>"
                                        ),
                                        Field.Switch(
                                            "enable_gradient",
                                            "Enable Gradient Mode",
                                            default=False,
                                        ),
                                        # Shown when gradient is enabled
                                        Components.ConditionalField(
                                            Layout.Section(
                                                "Gradient Settings",
                                                [
                                                    Field.Select(
                                                        "gradient_type",
                                                        "Gradient Type",
                                                        options=[
                                                            "Linear",
                                                            "Radial",
                                                            "Angular",
                                                        ],
                                                        default="Linear",
                                                    ),
                                                    Field.Int(
                                                        "gradient_angle",
                                                        "Angle (degrees)",
                                                        default=45,
                                                        min=0,
                                                        max=360,
                                                    ),
                                                ],
                                            ),
                                            depends_on="enable_gradient",
                                            value=True,
                                        ),
                                        # Shown when gradient is disabled
                                        Components.ConditionalField(
                                            Layout.Html(
                                                "<div style='padding: 1rem; background: #fef3c7; "
                                                "border-radius: 8px; color: #92400e; margin-top: 1rem;'>"
                                                "💡 Enable Gradient Mode to access gradient settings."
                                                "</div>"
                                            ),
                                            depends_on="enable_gradient",
                                            value=False,
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ]
                ),
            ]
        )

    def run(self, params, logger: PipelineLogger) -> bool:
        """Execute the color mixing pipeline."""

        def check_abort():
            if self.is_stopped:
                logger.warning("Pipeline aborted by user")
                return True
            return False

        def sleep(seconds: float) -> bool:
            """Interruptible sleep - returns True if aborted."""
            interval = 0.1  # Check every 100ms
            elapsed = 0.0
            while elapsed < seconds:
                if self.is_stopped:
                    return True
                time.sleep(min(interval, seconds - elapsed))
                elapsed += interval
            return False

        # Parse color selections
        raw_colors = params.get("colors", [])
        colors = set()
        for c in raw_colors:
            if "Red" in c:
                colors.add("Red")
            elif "Blue" in c:
                colors.add("Blue")
            elif "Yellow" in c:
                colors.add("Yellow")

        project_name = params.get("project_name", "Untitled")

        # ===== Stage 1: Analysis =====
        logger.stage("Color Analysis")
        logger.info(f"Project: {project_name}")

        with self.progress.step("Analyzing Colors") as step:
            if not colors:
                logger.warning("No colors selected - using default (Red)")
                colors = {"Red"}

            sleep(0.5)
            logger.info(f"Selected {len(colors)} primary color(s):")
            for color in sorted(colors):
                logger.indent(f"• {color}")
                sleep(0.4)
            sleep(0.3)
            step.message = f"{len(colors)} colors ready"

        if check_abort():
            return False

        # ===== Stage 2: Mixing =====
        logger.stage("Pigment Mixing")

        with self.progress.step("Mixing Pigments") as step:
            color_mixes = {
                frozenset(["Red", "Blue"]): ("Purple", "🟣"),
                frozenset(["Red", "Yellow"]): ("Orange", "🟠"),
                frozenset(["Blue", "Yellow"]): ("Green", "🟢"),
                frozenset(["Red", "Blue", "Yellow"]): ("Brown", "🟤"),
                frozenset(["Red"]): ("Red", "🔴"),
                frozenset(["Blue"]): ("Blue", "🔵"),
                frozenset(["Yellow"]): ("Yellow", "🟡"),
            }

            result_name, result_emoji = color_mixes.get(
                frozenset(colors), ("Gray", "⚫")
            )

            logger.step("Combining pigments...")
            sleep(0.8)
            logger.command(f"mix --colors {','.join(sorted(colors))}")
            sleep(1.0)
            logger.info("Calculating color ratios...")
            sleep(0.6)
            if check_abort():
                return False
            step.message = f"Base: {result_name}"

        # ===== Stage 3: Effects =====
        logger.stage("Applying Effects")

        with self.progress.step("Applying Effects") as step:
            # Build modifier string
            modifiers = []

            intensity = params.get("intensity", "Medium")
            if intensity == "Light":
                modifiers.append("Pale")
            elif intensity == "Vibrant":
                modifiers.append("Vivid")

            if params.get("add_white"):
                modifiers.append("Tinted")
            if params.get("add_black"):
                modifiers.append("Shaded")

            saturation = params.get("saturation", 75)
            opacity = params.get("opacity", 1.0)

            logger.info(f"Saturation: {saturation}%")
            sleep(0.4)
            logger.info(f"Opacity: {opacity}")
            sleep(0.4)

            if params.get("enable_gradient"):
                grad_type = params.get("gradient_type", "Linear")
                grad_angle = params.get("gradient_angle", 45)
                modifiers.append(f"{grad_type} Gradient")
                logger.info(f"Gradient: {grad_type} at {grad_angle}°")
                sleep(0.5)

            sleep(0.5)

            modifier_str = " ".join(modifiers)
            final_color = (
                f"{modifier_str} {result_name}".strip() if modifiers else result_name
            )
            step.message = f"Applied {len(modifiers)} effects"

        logger.success(f"{result_emoji} Final Result: {final_color}")

        if check_abort():
            return False

        # ===== Stage 4: Output =====
        logger.stage("Generating Output")

        with self.progress.step("Generating Output"):
            output_prefix = params.get("output_prefix", "color_mix")
            output_dir = Path(params.get("output_directory", ".")) / "color_outputs"
            output_dir.mkdir(parents=True, exist_ok=True)

            logger.info("Creating result file...")
            sleep(0.6)

            result_file = output_dir / f"{output_prefix}_result.txt"
            with open(result_file, "w") as f:
                f.write("🎨 Color Mix Result\n")
                f.write(f"{'=' * 40}\n\n")
                f.write(f"Project: {project_name}\n")
                f.write(f"Input Colors: {', '.join(sorted(colors))}\n")
                f.write(f"Intensity: {intensity}\n")
                f.write(f"Saturation: {saturation}%\n")
                f.write(f"Opacity: {opacity}\n\n")
                f.write(f"Result: {result_emoji} {final_color}\n")

                if notes := params.get("notes"):
                    f.write(f"\nNotes:\n{notes}\n")

            logger.success(f"Saved: {result_file}")
            sleep(0.5)

            # Bundle results
            logger.info("Packaging results...")
            sleep(0.4)
            bundle = ResultBundle(output_prefix, base_dir=output_dir)
            bundle.add_file(result_file.name, description="Color Mix Result")

            zip_path = bundle.create_zip()
            sleep(0.5)
            if zip_path:
                logger.info(f"📦 Download ready: {zip_path.name}")

        return True

    @action("color_theory")
    def show_color_theory(self, logger: PipelineLogger):
        """Display educational color theory information."""
        logger.stage("Color Theory Guide")

        logger.step("Primary Colors")
        logger.info("Cannot be created by mixing other colors:")
        logger.indent("🔴 Red")
        logger.indent("🔵 Blue")
        logger.indent("🟡 Yellow")
        time.sleep(0.5)

        logger.step("Secondary Colors")
        logger.info("Created by mixing two primaries:")
        logger.indent("🟣 Purple = Red + Blue")
        logger.indent("🟠 Orange = Red + Yellow")
        logger.indent("🟢 Green = Blue + Yellow")
        time.sleep(0.5)

        logger.step("Tertiary Colors")
        logger.info("Created by mixing all three primaries:")
        logger.indent("🟤 Brown = Red + Blue + Yellow")
        time.sleep(0.3)

        logger.step("Color Properties")
        logger.info("• Tint: Add white to lighten")
        logger.info("• Shade: Add black to darken")
        logger.info("• Saturation: Color intensity (0-100%)")

        logger.success("🎓 Color theory lesson complete!")
        return True


if __name__ == "__main__":
    pipeline = ColorMixerPipeline()
    print("Color Mixer Pipeline instantiated!")
    print(f"Features: {len(pipeline.progress.steps)} progress steps")
