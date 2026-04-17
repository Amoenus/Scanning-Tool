"""Domain models for the scanning tool configuration and state."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Literal, Optional, List, TypedDict, Union

if TYPE_CHECKING:
    from scanning_tool.services.config_service import ConfigData

# --- Raw JSON DTOs for RockType.json ---

OreTier = Literal["HIGHEST", "HIGH", "MEDIUM", "LOW", "OTHER"]


class OreStatisticsData(TypedDict, total=False):
    prob: float | str
    minPct: float | str
    maxPct: float | str
    medPct: float | str


class DepositData(TypedDict, total=False):
    users: int | str
    scans: int | str
    clusters: int | str
    clusterCount: Dict[str, float]
    mass: Dict[str, float]
    inst: Dict[str, float]
    res: Dict[str, float]
    ores: Dict[str, OreStatisticsData]


RegionData = Dict[str, DepositData]
RockDataJSON = Dict[str, RegionData]


class MssMonitor(TypedDict):
    """Monitor dict compatible with the mss library."""

    left: int
    top: int
    width: int
    height: int


@dataclass
class OreStatistics:
    """Per-ore stats inside a Deposit's `ores` map (loaded from RockType.json)."""

    prob: float
    minPct: float
    maxPct: float
    medPct: float

    @staticmethod
    def _to_float(value: int | float | str | None) -> float:
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return 0.0
        return 0.0

    @classmethod
    def from_dict(cls, data: OreStatisticsData) -> "OreStatistics":
        return cls(
            prob=cls._to_float(data.get("prob")),
            minPct=cls._to_float(data.get("minPct")),
            maxPct=cls._to_float(data.get("maxPct")),
            medPct=cls._to_float(data.get("medPct")),
        )


@dataclass
class Deposit:
    """A single deposit entry inside a region in RockType.json."""

    users: int
    scans: int
    clusters: int
    clusterCount: Dict[str, float]
    mass: Dict[str, float]
    inst: Dict[str, float]
    res: Dict[str, float]
    ores: Dict[str, OreStatistics]

    @staticmethod
    def _to_int(value: int | str | float | None) -> int:
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str):
            try:
                return int(float(value))
            except ValueError:
                return 0
        return 0

    @classmethod
    def from_dict(cls, data: DepositData) -> "Deposit":
        ores_data = data.get("ores", {})
        ores = {
            ore_name: OreStatistics.from_dict(ore_data)
            for ore_name, ore_data in ores_data.items()
            if isinstance(ore_data, dict)
        }

        return cls(
            users=cls._to_int(data.get("users")),
            scans=cls._to_int(data.get("scans")),
            clusters=cls._to_int(data.get("clusters")),
            clusterCount=data.get("clusterCount", {}),
            mass=data.get("mass", {}),
            inst=data.get("inst", {}),
            res=data.get("res", {}),
            ores=ores,
        )


@dataclass
class Region:
    """A collection of deposits for a given region."""

    deposits: Dict[str, Deposit]

    @classmethod
    def from_dict(cls, data: RegionData) -> "Region":
        deposits = {
            deposit_name: Deposit.from_dict(deposit_data)
            for deposit_name, deposit_data in data.items()
            if isinstance(deposit_data, dict)
        }
        return cls(deposits=deposits)


@dataclass
class RockDataCollection:
    """Top-level container for all region data."""

    regions: Dict[str, Region] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: RockDataJSON) -> "RockDataCollection":
        regions = {
            region_name: Region.from_dict(region_data)
            for region_name, region_data in data.items()
            if isinstance(region_data, dict)
        }
        return cls(regions=regions)


RockData = RockDataCollection  # Alias for backward compatibility during refactor


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


class SignatureRegistry:
    """Domain service to manage a registry of ScanSignatures."""

    def __init__(self, signatures: Optional[Dict[int, ScanSignature]] = None):
        self._signatures = signatures or {}

    def add(self, signature: ScanSignature) -> None:
        self._signatures[signature.base_value] = signature

    def get(self, base_value: int) -> Optional[ScanSignature]:
        return self._signatures.get(base_value)

    def get_all(self) -> Dict[int, ScanSignature]:
        return self._signatures.copy()

    @classmethod
    def load_from_csv(cls, path: str | Path) -> "SignatureRegistry":
        from pathlib import Path
        from scanning_tool.deposits.scan_signatures import _load_scan_signatures

        return _load_scan_signatures(Path(path))


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

    def reset(self) -> None:
        """Clear the alignment result state for a fresh evaluation."""
        self.matched = False
        self.template = None
        self.score = 0.0
        self.match_left = None
        self.match_top = None
        self.capture_left = None
        self.capture_top = None

    def update_from_detection(
        self, detection: "AnchorDetection", capture_region: "CaptureRegion"
    ) -> None:
        """Update this alignment state from a successful anchor detection."""
        self.matched = True
        self.template = detection.template
        self.score = detection.score
        self.match_left = int(round(detection.match_left))
        self.match_top = int(round(detection.match_top))
        self.capture_left = capture_region.left
        self.capture_top = capture_region.top


@dataclass(frozen=True)
class AlignmentRequest:
    """Request payload containing the inputs required for an alignment run."""

    enabled: bool
    threshold: float
    anchor_template: "CaptureRegion"
    anchor_offset: "Offset2D"
    capture_region: "CaptureRegion"

    @classmethod
    def from_config(cls, config: "ConfigData") -> "AlignmentRequest":
        return cls(
            enabled=config.auto_alignment.enabled,
            threshold=float(config.anchor_threshold),
            anchor_template=config.anchor_template,
            anchor_offset=config.anchor_offset,
            capture_region=config.capture_region,
        )


@dataclass
class CaptureRegion:
    """Represents a capture region on the screen."""

    left: int
    top: int
    width: int
    height: int

    def to_mss_monitor(self) -> dict[str, int]:
        """Return an mss-compatible monitor dict for this region."""
        return {
            "left": int(self.left),
            "top": int(self.top),
            "width": int(self.width),
            "height": int(self.height),
        }

    def to_tuple(self) -> tuple[int, int, int, int]:
        """Return an mss-compatible tuple representation for this region."""
        return (self.left, self.top, self.width, self.height)


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
    last: Optional["ScanResult"]
    alignment: "AlignmentInfo"
    selected_region: str
    info: Optional[DepositInfo]
    code: Optional[str]
    code_raw: Optional[str]
    raw_text: Optional[str]
    table: Optional[DepositTable]

    def to_dict(self) -> dict:
        from dataclasses import asdict

        return asdict(self)
