"""Interface definitions package."""

from .capture import (
    AlignmentAdapter,
    CaptureProvider,
    DepositLookupProvider,
    OCRProvider,
    StatusCallback,
)
from .capture_service import CaptureController

__all__ = [
    "AlignmentAdapter",
    "CaptureController",
    "CaptureProvider",
    "DepositLookupProvider",
    "OCRProvider",
    "StatusCallback",
]
