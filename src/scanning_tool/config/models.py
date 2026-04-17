"""Configuration models for the scanning tool."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from scanning_tool.domain.models import CaptureRegion, Offset2D


@dataclass
class OverlayConfig:
    """Represents overlay display configuration."""

    info_offset: Offset2D
    label_color: str
    show_debug: bool


@dataclass
class OllamaConfig:
    """Represents Ollama AI service configuration."""

    model: str
    host: Optional[str]


@dataclass
class AutoAlignmentConfig:
    """Represents auto-alignment configuration."""

    enabled: bool
    poll_interval_ms: int
    anchor_region: CaptureRegion


@dataclass
class ContinuousCaptureConfig:
    """Represents continuous capture configuration."""

    interval: float


@dataclass
class WebServerConfig:
    """Represents the Flask web server configuration."""

    host: str = "0.0.0.0"
    port: int = 5000
