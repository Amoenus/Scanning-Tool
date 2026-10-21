from typing import Any
from pydantic import BaseModel, model_validator


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


class RegionSelectPayload(BaseModel):
    region: str | None = None


class RegionDragPayload(BaseModel):
    left: int | None = None
    top: int | None = None
    width: int | None = None
    height: int | None = None
    x: int | None = None
    y: int | None = None
    delta_left: int | None = None
    delta_top: int | None = None
    delta_width: int | None = None
    delta_height: int | None = None
    delta_x: int | None = None
    delta_y: int | None = None

    @model_validator(mode="before")
    @classmethod
    def _coerce_int_like(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        coerced = {}
        for k, v in data.items():
            if isinstance(v, (int, float)):
                coerced[k] = int(v)
            elif isinstance(v, str) and v.lstrip("-").isdigit():
                coerced[k] = int(v)
            elif v is None:
                coerced[k] = None
        return coerced
