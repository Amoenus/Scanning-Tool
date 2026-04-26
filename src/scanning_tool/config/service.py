"""Configuration persistence service for the scanning tool."""

import json
from pathlib import Path
from typing import Optional, Protocol

from loguru import logger
from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from scanning_tool.config.models import (
    AutoAlignmentConfig,
    OllamaConfig,
    OverlayConfig,
    WebServerConfig,
)
from scanning_tool.domain.alignment import CaptureRegion
from scanning_tool.domain.common import Offset2D

DEFAULT_CONFIG_FILE = Path(__file__).resolve().parents[3] / "config.json"


class ConfigData(BaseSettings):
    """Typed settings for the scanning tool."""

    model_config = SettingsConfigDict(
        arbitrary_types_allowed=True,
        extra="ignore",
        env_prefix="",
        env_nested_delimiter="__",
    )

    capture_region: CaptureRegion = Field(
        default_factory=lambda: CaptureRegion(1260, 310, 160, 30)
    )
    overlay_config: OverlayConfig = Field(
        default_factory=lambda: OverlayConfig(Offset2D(0, 0), "yellow", True)
    )
    auto_alignment: AutoAlignmentConfig = Field(
        default_factory=lambda: AutoAlignmentConfig(
            True, 500, CaptureRegion(1100, 240, 320, 140)
        )
    )
    anchor_template: CaptureRegion = Field(
        default_factory=lambda: CaptureRegion(1100, 240, 320, 140)
    )
    anchor_offset: Offset2D = Field(default_factory=lambda: Offset2D(36, 56))
    anchor_threshold: float = 0.82
    anchor_template_dir: str = "assets/anchor_templates"
    alignment_poll_interval_ms: int = 500
    continuous_capture_interval: float = 2.0
    ollama_config: OllamaConfig = Field(default_factory=lambda: OllamaConfig("", None))
    web_server_config: WebServerConfig = Field(
        default_factory=lambda: WebServerConfig("0.0.0.0", 5000)
    )
    gui_backend: str = "tk"


class ConfigSaver(Protocol):
    """Minimal config persistence contract."""

    def save(self) -> None: ...


class ConfigService:
    """Service for loading, saving, and managing configuration."""

    def __init__(self, config_file: Optional[Path] = None):
        self.config_file = config_file or DEFAULT_CONFIG_FILE
        self._config: Optional[ConfigData] = None

    def load(self) -> ConfigData:
        """Load configuration from file."""
        try:
            self._config = self._load_config_from_file()
            return self._config
        except FileNotFoundError:
            logger.info(
                "Configuration file not found, creating default.",
                path=str(self.config_file),
            )
            self._config = self._create_default_config()
            return self._config
        except (json.JSONDecodeError, OSError, ValidationError) as exc:
            logger.warning(
                "Failed to load configuration, using defaults.",
                path=str(self.config_file),
                error=exc,
            )
            self._config = self._create_default_config()
            return self._config

    def _create_default_config(self) -> ConfigData:
        config = ConfigData()
        self._config = config
        self.save()
        return config

    def _load_config_from_file(self) -> ConfigData:
        with self.config_file.open("r", encoding="utf-8") as config_file:
            raw_data = json.load(config_file)
        return ConfigData(**raw_data)

    def save(self) -> None:
        """Save configuration to file."""
        if self._config is None:
            raise ValueError("No configuration to save")

        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            self.config_file.write_text(
                json.dumps(self._config.model_dump(mode="json"), indent=4) + "\n",
                encoding="utf-8",
            )
            logger.info("Configuration saved successfully.")
        except OSError as exc:
            logger.error(f"Failed to save configuration: {exc}")

    def get_config(self) -> ConfigData:
        """Get the current configuration.

        The configuration must be loaded explicitly via `load()` before access.
        """
        if self._config is None:
            raise ValueError("Configuration has not been loaded")
        return self._config

    def get_capture_region(self) -> CaptureRegion:
        """Get the capture region configuration."""
        return self.get_config().capture_region

    def get_ollama_config(self) -> OllamaConfig:
        """Get the Ollama configuration."""
        return self.get_config().ollama_config

    def get_auto_alignment_config(self) -> AutoAlignmentConfig:
        """Get the auto-alignment configuration."""
        return self.get_config().auto_alignment

    def get_overlay_config(self) -> OverlayConfig:
        """Get the overlay configuration."""
        return self.get_config().overlay_config
