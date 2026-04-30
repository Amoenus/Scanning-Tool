from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scanning_tool.domain.alignment import AlignmentInfo


@dataclass(frozen=True)
class RuntimeStatusModel:
    """Read model for the Runtime status concern."""

    global_status_message: str = "Initializing..."
    alignment_info: AlignmentInfo | None = None
    ollama_message: str = "Waiting for Ollama status."
    ollama_model: str | None = None
    ollama_host: str | None = None
    ollama_ready: bool | None = None
