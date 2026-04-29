from dataclasses import dataclass
from typing import Optional

from scanning_tool.domain.models import ScanResult


@dataclass(frozen=True)
class LatestScan:
    """Read model for the Scan result concern."""

    result: Optional[ScanResult] = None
    is_scanning: bool = False
    continuous_mode_enabled: bool = False
    error: Optional[str] = None
