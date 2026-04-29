from dataclasses import dataclass
from typing import Optional

from scanning_tool.domain.alignment import AlignmentInfo


@dataclass(frozen=True)
class RuntimeStatusModel:
    """Read model for the Runtime status concern."""

    global_status_message: str = "Initializing..."
    alignment_info: Optional[AlignmentInfo] = None
    ollama_message: str = "Waiting for Ollama status."
    ollama_model: Optional[str] = None
    ollama_host: Optional[str] = None
    ollama_ready: Optional[bool] = None
