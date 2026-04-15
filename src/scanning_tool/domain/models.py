"""Domain models for the scanning tool configuration and state."""

from dataclasses import dataclass, field
from typing import Dict, Literal, Optional, List, Tuple, Any, TypedDict, Union

# --- Deposit / ore DTOs ---

OreTier = Literal["HIGHEST", "HIGH", "MEDIUM", "LOW", "OTHER"]


class OreInfo(TypedDict):
    """Per-ore stats inside a RockDeposit's `ores` map (loaded from RockType.json)."""
    prob: float
    minPct: float
    maxPct: float
    medPct: float


class RockDeposit(TypedDict, total=False):
    """A single deposit entry inside a region in RockType.json."""
    users: int
    scans: int
    clusters: int
    clusterCount: Dict[str, float]
    mass: Dict[str, float]
    inst: Dict[str, float]
    res: Dict[str, float]
    ores: Dict[str, OreInfo]


# Region name -> deposit name -> RockDeposit (raw RockType.json shape).
RockData = Dict[str, Dict[str, RockDeposit]]


class OreValueInfo(TypedDict):
    """Tier classification + display color for an ore."""
    tier: OreTier
    color: str


class OreTableEntry(TypedDict):
    """A row in a per-region deposit table, ready for display/serialization."""
    name: str
    prob: str
    min: str
    max: str
    med: str
    tier: OreTier
    color: str


# Per-deposit ordered list of ore rows.
DepositTable = List[OreTableEntry]
# Region (uppercase) -> deposit name (uppercase) -> DepositTable.
RegionDepositTables = Dict[str, Dict[str, DepositTable]]


class ScanSignature(TypedDict):
    """An entry in SCAN_SIGNATURES, keyed by base_value."""
    name: str
    category: str
    base_value: int
    max_multiplier: int


class DepositLookup(TypedDict):
    """Result of resolving a numeric scan code against SCAN_SIGNATURES."""
    name: str
    base_code: int
    deposits: int
    category: str
    max_multiplier: int


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
    base_code: Optional[int] = None
    deposits: Optional[int] = None
    max_multiplier: Optional[int] = None


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
    """A single scan result — the cleaned code (`label`), the raw OCR text it came from, and resolved deposit metadata."""
    label: str
    confidence: float
    region: CaptureRegion
    info: Optional[DepositInfo] = None
    code_raw: Optional[str] = None
    raw_text: Optional[str] = None


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
