"""Domain models for the scanning tool configuration and state."""

from dataclasses import dataclass, field
from typing import Dict, Optional, List, Tuple, Any, Union
# --- New Structured Domain Models ---

@dataclass
class DepositInfo:
    """
    Structured metadata for a detected deposit or scan signature.
    Fields correspond to common keys found in legacy info dicts (e.g., key, name, category, type, id).
    Use this for type-safe access to scan/deposit metadata instead of unstructured dicts.
    """
    key: Optional[str] = None
    name: Optional[str] = None
    category: Optional[str] = None
    type: Optional[str] = None
    id: Optional[Union[str, int]] = None
    extra: Optional[Dict[str, Any]] = None


# Placeholder for AnchorTracker structure (to be refined if more details are known)
@dataclass
class AnchorTracker:
    """
    Represents the anchor tracking state.
    This is a placeholder; add fields as anchor tracking logic is formalized.
    """
    templates: List[Any] = field(default_factory=list)
    last_loaded_count: int = 0
    # Add more fields as needed based on actual usage


# More explicit AlignmentInfo (moved from runtime/scan_state.py for typing clarity)
@dataclass
class AlignmentInfo:
    """
    Represents the current alignment state for anchor/template matching.
    Use explicit types for all fields to improve reliability and clarity.
    """
    enabled: bool = True
    matched: bool = False
    template: Optional[str] = None
    score: float = 0.0
    match_left: Optional[int] = None
    match_top: Optional[int] = None
    capture_left: Optional[int] = None
    capture_top: Optional[int] = None


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
    """
    Represents a single scan result (e.g., detected deposit or signature).
    Use the 'info' field for structured metadata (DepositInfo),
    and 'extra' for legacy/unstructured data if needed.
    """
    label: str
    confidence: float
    region: CaptureRegion
    info: Optional[DepositInfo] = None  # Structured metadata for the result
    extra: Optional[Dict[str, Any]] = None  # For extensibility (legacy/unstructured)


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
