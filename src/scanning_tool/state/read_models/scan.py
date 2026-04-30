from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scanning_tool.domain.models import ScanResult


@dataclass(frozen=True)
class LatestScan:
    """Read model for the Scan result concern."""

    result: ScanResult | None = None
    is_scanning: bool = False
    continuous_mode_enabled: bool = False
    error: str | None = None
