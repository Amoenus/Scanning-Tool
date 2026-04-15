

from dataclasses import dataclass, field
from typing import Any
# LastResult is now replaced by ScanResult in domain.models

@dataclass
class AlignmentInfo:
    enabled: bool = True
    matched: bool = False
    template: Any = None
    score: float = 0.0
    match_left: Any = None
    match_top: Any = None
    capture_left: Any = None
    capture_top: Any = None

