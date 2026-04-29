from dataclasses import dataclass

@dataclass(frozen=True)
class EditModeReadModel:
    """Read model for the Edit mode concern."""
    is_edit_mode: bool = False
