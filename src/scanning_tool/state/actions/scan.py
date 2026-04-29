from enum import StrEnum

class ScanAction(StrEnum):
    """Actions for the Scan result concern."""
    SINGLE_SCAN = "single_scan"
    TOGGLE_CONTINUOUS_CAPTURE = "toggle_continuous_capture"
