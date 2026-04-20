
from scanning_tool.config.service import ConfigData
from scanning_tool.gui.provider import get_default_gui_provider


def test_config_data_accepts_gui_backend():
    config = ConfigData(gui_backend="qt")

    assert config.gui_backend == "qt"


def test_get_default_gui_provider_prefers_config():
    config = ConfigData(gui_backend="tk")
    provider = get_default_gui_provider(config)

    assert provider.provider_name == "tk"


def test_get_default_gui_provider_fallbacks_to_tk_for_unknown_config_backend():
    config = ConfigData(gui_backend="unknown-backend")

    provider = get_default_gui_provider(config)

    assert provider.provider_name == "tk"


def test_get_default_gui_provider_uses_default_when_no_config():
    provider = get_default_gui_provider()

    assert provider.provider_name == "tk"
