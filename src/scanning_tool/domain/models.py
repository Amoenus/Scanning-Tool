"""Domain models for the scanning tool configuration and state."""

from dataclasses import dataclass, field
from typing import Dict, Literal, Optional, List, Tuple, TypedDict, Union

# --- Deposit / ore DTOs ---

OreTier = Literal["HIGHEST", "HIGH", "MEDIUM", "LOW", "OTHER"]


class OreInfo(TypedDict):
    """Per-ore stats inside a RockDeposit's `ores` map (loaded from RockType.json)."""
    prob: float
    minPct: float
    maxPct: float
    medPct: float


@dataclass(frozen=True)
class OreInfoModel:
    """Structured ore concentration data extracted from raw RockType JSON."""
    prob: float = 0.0
    min_pct: float = 0.0
    max_pct: float = 0.0
    med_pct: float = 0.0

    @classmethod
    def from_raw(cls, raw: OreInfo) -> "OreInfoModel":
        return cls(
            prob=raw.get("prob", 0.0),
            min_pct=raw.get("minPct", 0.0),
            max_pct=raw.get("maxPct", 0.0),
            med_pct=raw.get("medPct", 0.0),
        )

    def format_pct(self, value: float) -> str:
        return f"{value * 100:.0f}%"

    @property
    def prob_pct(self) -> str:
        return self.format_pct(self.prob)

    @property
    def min_pct_str(self) -> str:
        return self.format_pct(self.min_pct)

    @property
    def max_pct_str(self) -> str:
        return self.format_pct(self.max_pct)

    @property
    def med_pct_str(self) -> str:
        return self.format_pct(self.med_pct)


class MssMonitor(TypedDict):
    """Monitor dict compatible with the mss library."""
    left: int
    top: int
    width: int
    height: int


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


@dataclass(frozen=True)
class OreValueInfo:
    """Tier classification + display color for an ore."""
    tier: OreTier
    color: str


@dataclass
class OreTableEntry:
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


@dataclass(frozen=True)
class ScanSignature:
    """An entry in SCAN_SIGNATURES, keyed by base_value."""
    name: str
    category: str
    base_value: int
    max_multiplier: int


# --- Shared Value Types ---

@dataclass
class Offset2D:
    """A 2D offset with x and y components."""
    x: int = 0
    y: int = 0


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

    def to_mss_monitor(self) -> 'MssMonitor':
        """Return an mss-compatible monitor dict for this region."""
        return MssMonitor(
            left=int(self.left),
            top=int(self.top),
            width=int(self.width),
            height=int(self.height),
        )


@dataclass
class OverlayConfig:
    """Represents overlay display configuration."""
    info_offset: Offset2D
    label_color: str
    show_debug: bool


OLLAMA_DEFAULT_HOST = "http://127.0.0.1:11434"


@dataclass
class OllamaConfig:
    """Represents Ollama AI service configuration."""
    model: str
    host: Optional[str]


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


@dataclass
class WebServerConfig:
    """Represents the Flask web server configuration."""
    host: str = "0.0.0.0"
    port: int = 5000


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
class AnchorDetection:
    """Result of an anchor template match on a captured region."""
    match_left: float
    match_top: float
    score: float
    template: str
    template_width: float
    template_height: float


@dataclass
class OreTierInfo:
    """Ores belonging to a tier plus its display color."""
    ores: List[str]
    color: str


@dataclass
class InfoOverlayGeometry:
    """Geometry snapshot for the info overlay window."""
    screen_width: Optional[int] = None
    screen_height: Optional[int] = None
    width: int = 0
    height: int = 0


@dataclass
class CaptureOverlayLayout:
    """Layout values for positioning and sizing the capture overlay."""
    overlay_width: int
    overlay_height: int
    left: int
    top: int
    padding_x: int
    padding_y: int
    cap_w: int
    cap_h: int


@dataclass
class AnchorOverlayGeometry:
    """Geometry for the anchor overlay window."""
    width: int
    height: int
    left: int
    top: int


@dataclass(frozen=True)
class ModelPromptProfile:
    """Maps an Ollama model name prefix to its OCR prompt."""
    prefix: str
    prompt: str


@dataclass
class InfoOverlayLayout:
    """Computed position and size for the floating info overlay."""
    width: int
    height: int
    left: int
    top: int


@dataclass(frozen=True)
class GlassPalette:
    """Theme color palette — frozen to prevent accidental mutation."""
    background: str
    panel: str
    accent: str
    text: str
    muted: str
    button: str
    button_hover: str
    border: str
    glow: str
    knob: str
    knob_active: str
    knob_outline: str


@dataclass
class CodeExtraction:
    """Output of parsing a deposit code from OCR text."""
    code: Optional[str]
    raw: Optional[str]


@dataclass
class StatusResponse:
    """Payload returned by the /status web endpoint."""
    region: CaptureRegion
    label_color: str
    last: Optional['ScanResult']
    alignment: 'AlignmentInfo'
    selected_region: str
    info: Optional[DepositInfo]
    code: Optional[str]
    code_raw: Optional[str]
    confidence: Optional[float]
    raw_text: Optional[str]
    table: Optional[DepositTable]

    def to_dict(self) -> dict:
        from dataclasses import asdict
        return asdict(self)
