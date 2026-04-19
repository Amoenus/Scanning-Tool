"""Interface definitions package."""

from .capture import (
    AlignmentAdapter,
    CaptureProvider,
    DepositLookupProvider,
    OCRProvider,
    StatusCallback,
    SyncCallback,
)

__all__ = [
    "AlignmentAdapter",
    "CaptureProvider",
    "DepositLookupProvider",
    "OCRProvider",
    "StatusCallback",
    "SyncCallback",
]
