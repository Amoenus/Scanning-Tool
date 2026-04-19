from pathlib import Path

import pytest

from scanning_tool.config.service import ConfigService, ConfigData
from scanning_tool.state.app_state import AppState


def test_app_state_is_instantiated_with_config(tmp_path: Path) -> None:
    config_file = tmp_path / "config.json"
    service = ConfigService(config_file=config_file)

    loaded_config = service.load()
    app_state = AppState(config=loaded_config)

    assert isinstance(app_state.config, ConfigData)
    assert app_state.config is loaded_config
    assert config_file.exists()


def test_config_service_requires_load_before_access(tmp_path: Path) -> None:
    service = ConfigService(config_file=tmp_path / "config.json")

    with pytest.raises(ValueError, match="Configuration has not been loaded"):
        service.get_config()

    config = service.load()
    assert isinstance(config, ConfigData)
    assert config is service.get_config()
