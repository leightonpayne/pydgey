"""Widget package for interactive pipeline execution.

This package provides the PipelineWidget and related utilities
for rendering and controlling pipelines in Jupyter notebooks.
"""

from .base import PipelineWidget, create_launcher
from .transport import create_transport, WidgetTransport

__all__ = [
    "PipelineWidget",
    "create_launcher",
    "create_transport",
    "WidgetTransport",
]
