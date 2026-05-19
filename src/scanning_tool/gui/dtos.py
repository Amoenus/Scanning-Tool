from __future__ import annotations

from dataclasses import dataclass

@dataclass(slots=True, kw_only=True, frozen=True)
class RegionPayloadDTO:
    left: int | None = None
    top: int | None = None
    width: int | None = None
    height: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> RegionPayloadDTO:
        def _parse_int(val: object) -> int | None:
            if val is None:
                return None
            try:
                return int(val) # type: ignore[arg-type]
            except (TypeError, ValueError):
                return None

        return cls(
            left=_parse_int(data.get("left")),
            top=_parse_int(data.get("top")),
            width=_parse_int(data.get("width")),
            height=_parse_int(data.get("height")),
        )


@dataclass(slots=True, kw_only=True, frozen=True)
class OffsetPayloadDTO:
    x: int | None = None
    y: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> OffsetPayloadDTO:
        def _parse_int(val: object) -> int | None:
            if val is None:
                return None
            try:
                return int(val) # type: ignore[arg-type]
            except (TypeError, ValueError):
                return None

        return cls(
            x=_parse_int(data.get("x")),
            y=_parse_int(data.get("y")),
        )


@dataclass(slots=True, kw_only=True, frozen=True)
class TogglePayloadDTO:
    visible: bool | None = None
    enabled: bool | None = None

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> TogglePayloadDTO:
        return cls(
            visible=bool(data.get("visible")) if "visible" in data else None,
            enabled=bool(data.get("enabled")) if "enabled" in data else None,
        )


@dataclass(slots=True, kw_only=True, frozen=True)
class ValuePayloadDTO:
    value: object | None = None

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> ValuePayloadDTO:
        return cls(value=data.get("value"))


@dataclass(slots=True, kw_only=True, frozen=True)
class UrlPayloadDTO:
    url: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> UrlPayloadDTO:
        return cls(url=str(data.get("url", "")))


@dataclass(slots=True, kw_only=True, frozen=True)
class OllamaPayloadDTO:
    host: str = ""
    model: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> OllamaPayloadDTO:
        return cls(
            host=str(data.get("host", "")),
            model=str(data.get("model", "")),
        )
