"""DTO models for GUI action payloads."""
from pydantic import BaseModel, ConfigDict


class PayloadBase(BaseModel):
    """Base model for all action payloads."""

    model_config = ConfigDict(extra="ignore")


class TogglePayload(PayloadBase):
    """Payload for boolean toggle actions."""

    enabled: bool = False
    visible: bool = False


class RegionUpdatePayload(PayloadBase):
    """Payload for region bound updates."""

    left: int | None = None
    top: int | None = None
    width: int | None = None
    height: int | None = None


class OffsetUpdatePayload(PayloadBase):
    """Payload for x/y coordinate updates."""

    x: int | None = None
    y: int | None = None


class ValueUpdatePayload(PayloadBase):
    """Payload for numerical value updates."""

    value: float | None = None


class UrlPayload(PayloadBase):
    """Payload for URL actions."""

    url: str = ""


class OllamaModelPayload(PayloadBase):
    """Payload for Ollama model selection."""

    model: str = ""


class OllamaHostPayload(PayloadBase):
    """Payload for Ollama host selection."""

    host: str = ""
