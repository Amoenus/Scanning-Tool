from dataclasses import dataclass, field
from enum import StrEnum


class ActiveRegion(StrEnum):
    CAPTURE = "capture"
    ANCHOR = "anchor"
    INFO = "info"


@dataclass(kw_only=True)
class ActiveRegionState:
    """Domain model representing coordinates/offsets of an active region."""

    left: int | None = None
    top: int | None = None
    width: int | None = None
    height: int | None = None
    x: int | None = None
    y: int | None = None

    def to_payload_dict(self) -> dict[str, int]:
        """Convert to unstructured int dictionary for UI signaling payload."""
        result: dict[str, int] = {}
        if self.left is not None:
            result["left"] = self.left
        if self.top is not None:
            result["top"] = self.top
        if self.width is not None:
            result["width"] = self.width
        if self.height is not None:
            result["height"] = self.height
        if self.x is not None:
            result["x"] = self.x
        if self.y is not None:
            result["y"] = self.y
        return result


@dataclass(frozen=True)
class EditModeReadModel:
    """Read model for the Edit mode concern."""

    is_edit_mode: bool = False
    active_region: ActiveRegion | None = None
    toolbar_visible: bool = False
    original_region_payload: dict[ActiveRegion, ActiveRegionState] = field(default_factory=dict)
