from enum import StrEnum

class EditModeAction(StrEnum):
    """Actions for the Edit mode concern."""
    ENTER_EDIT_MODE = "enter_edit_mode"
    EXIT_EDIT_MODE = "exit_edit_mode"
    DRAG_REGION = "drag_region"
    NUDGE_REGION = "nudge_region"
    CYCLE_REGION = "cycle_region"
    COMMIT_REGION = "commit_region"
