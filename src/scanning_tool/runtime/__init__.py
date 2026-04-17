"""Compatibility shim for runtime state.

The runtime package previously exposed the service state model. This shim preserves
existing import paths while the state package is consolidated.
"""

from scanning_tool.state.service_state import ServiceState

__all__ = ["ServiceState"]
