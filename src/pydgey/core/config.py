"""Pipeline configuration dataclasses."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class PipelineConfig:
    """Configuration metadata for the pipeline.

    This configuration controls the header and meta-information displayed
    in the [PipelineWidget](../api/widget.md).

    Attributes:
        name (str): Internal identifier for the pipeline. Defaults to "Pipeline".
        title (str): Large display title shown in the widget header. Defaults to "Pipeline Launcher".
        subtitle (str): Smaller description text shown below the title.
    """

    name: str = "Pipeline"
    title: str = "Pipeline Launcher"
    subtitle: str = ""
    actions: Optional[List[Dict[str, Any]]] = None
