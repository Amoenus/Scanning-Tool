"""Domain models for the scanning tool configuration and state."""

from dataclasses import dataclass
from typing import Dict, Optional, List, Tuple, Any


@dataclass
class CaptureRegion:
    """Represents a capture region on the screen."""
    left: int
    top: int
    width: int
    height: int


@dataclass
class AnchorTemplate:
    """Represents an anchor template configuration."""
    offset: Dict[str, int]
    threshold: float
    template_dir: str


@dataclass
class OverlayConfig:
    """Represents overlay display configuration."""
    info_offset: Dict[str, int]
    label_color: str
    show_debug: bool


@dataclass
class OllamaConfig:
    """Represents Ollama AI service configuration."""
    model: str
    host: Optional[str]
    default_host: str = "http://127.0.0.1:11434"


@dataclass
class ScanConfig:
    """Represents scanning configuration."""
    min_confidence: float


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


# --- Additional Domain Models / DTOs ---

@dataclass
class ScanResult:
    """Represents a single scan result (e.g., detected deposit or signature)."""
    label: str
    confidence: float
    region: CaptureRegion
    extra: Optional[Dict[str, Any]] = None  # For extensibility (e.g., type, id, etc.)


@dataclass
class OCRResult:
    """Represents the result of an OCR operation."""
    text: str
    confidence: float
    region: CaptureRegion


@dataclass
class HotkeyAction:
    """Represents a user action/command triggered by a hotkey."""
    name: str
    key_combo: str
    description: Optional[str] = None


@dataclass
class ToolStateSnapshot:
    """Represents a snapshot of the tool’s state (for saving/loading)."""
    timestamp: float
    active_scan: Optional[ScanResult]
    scan_history: List[ScanResult]
    config: Dict[str, Any]


@dataclass
class ErrorInfo:
    """Represents structured error information."""
    message: str
    code: Optional[str] = None
    details: Optional[Any] = None
