from pydantic import BaseModel

class TogglePayload(BaseModel):
    visible: bool | None = None
    enabled: bool | None = None

class RegionUpdatePayload(BaseModel):
    left: int | None = None
    top: int | None = None
    width: int | None = None
    height: int | None = None

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

class RegionDragPayload(BaseModel):
    left: int | None = None
    top: int | None = None
    width: int | None = None
    height: int | None = None
    delta_left: int | None = None
    delta_top: int | None = None
    delta_width: int | None = None
    delta_height: int | None = None
    x: int | None = None
    y: int | None = None
    delta_x: int | None = None
    delta_y: int | None = None

class RegionSelectPayload(BaseModel):
    region: str | None = None
