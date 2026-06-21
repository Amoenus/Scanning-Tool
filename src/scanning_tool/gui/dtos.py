from pydantic import BaseModel

class TogglePayload(BaseModel):
    visible: bool | None = None
    enabled: bool | None = None

class RegionUpdatePayload(BaseModel):
    left: int | None = None
    top: int | None = None
    width: int | None = None
    height: int | None = None

class EditModePayload(BaseModel):
    region: str | None = None
    left: int | float | None = None
    top: int | float | None = None
    width: int | float | None = None
    height: int | float | None = None
    x: int | float | None = None
    y: int | float | None = None
    delta_left: int | float | None = None
    delta_top: int | float | None = None
    delta_width: int | float | None = None
    delta_height: int | float | None = None
    delta_x: int | float | None = None
    delta_y: int | float | None = None

class OffsetUpdatePayload(BaseModel):
    x: int | None = None
    y: int | None = None

class ValueUpdatePayload(BaseModel):
    value: float | None = None

class UrlPayload(BaseModel):
    url: str | None = None

class OllamaModelPayload(BaseModel):
    model: str | None = None

class OllamaHostPayload(BaseModel):
    host: str | None = None
