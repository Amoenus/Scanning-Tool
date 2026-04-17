from pathlib import Path

import pytest

from scanning_tool.config.service import ConfigService, ConfigData
from scanning_tool.state.app_state import AppState


def test_app_state_loads_config_explicitly(tmp_path: Path) -> None:
    config_file = tmp_path / "config.json"
    service = ConfigService(config_file=config_file)
    app_state = AppState(config_service=service)

    assert app_state.config is None

    loaded_config = app_state.load_config()
    assert isinstance(loaded_config, ConfigData)
    assert loaded_config is service.get_config()
    assert config_file.exists()


def test_config_service_requires_load_before_access(tmp_path: Path) -> None:
    service = ConfigService(config_file=tmp_path / "config.json")

    with pytest.raises(ValueError, match="Configuration has not been loaded"):
        service.get_config()

    config = service.load()
    assert isinstance(config, ConfigData)
    assert config is service.get_config()
