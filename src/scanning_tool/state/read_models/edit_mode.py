from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scanning_tool.gui.dtos import EditModePayload


class ActiveRegion(StrEnum):
    CAPTURE = "capture"
    ANCHOR = "anchor"
    INFO = "info"


@dataclass(frozen=True)
class EditModeReadModel:
    """Read model for the Edit mode concern."""

    is_edit_mode: bool = False
    active_region: ActiveRegion | None = None
    toolbar_visible: bool = False
    original_region_payload: dict[ActiveRegion, "EditModePayload"] = field(default_factory=dict)
