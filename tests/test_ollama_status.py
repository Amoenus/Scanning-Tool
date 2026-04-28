from scanning_tool.gui.tk.sections.ollama import OllamaModelManager
from scanning_tool.ollama.status import publish_ollama_status
from scanning_tool.state.signals import ollama_readiness_changed, ollama_status_updated


def test_publish_ollama_status_emits_signals() -> None:
    received_status = []
    received_readiness = []

    def on_status(sender: object, **kwargs: object) -> None:
        received_status.append(kwargs)

    def on_readiness(sender: object, **kwargs: object) -> None:
        received_readiness.append(kwargs)

    ollama_status_updated.connect(on_status, weak=False)
    ollama_readiness_changed.connect(on_readiness, weak=False)

    publish_ollama_status(
        "Ollama ready",
        model="test-model",
        host="http://127.0.0.1:11434",
        ready=True,
    )

    assert len(received_status) == 1
    assert received_status[0]["message"] == "Ollama ready"
    assert received_status[0]["model"] == "test-model"
    assert received_status[0]["host"] == "http://127.0.0.1:11434"
    assert received_status[0]["ready"] is True

    assert len(received_readiness) == 1
    assert received_readiness[0]["model"] == "test-model"
    assert received_readiness[0]["ready"] is True

    ollama_status_updated.disconnect(on_status)
    ollama_readiness_changed.disconnect(on_readiness)


def test_apply_model_emits_ollama_status_signal(monkeypatch) -> None:
    received = []

    def on_status(sender: object, **kwargs: object) -> None:
        received.append(kwargs)

    ollama_status_updated.connect(on_status, weak=False)

    monkeypatch.setattr(
        "scanning_tool.gui.tk.sections.ollama.set_configured_ollama_model",
        lambda value: value,
    )
    monkeypatch.setattr(
        "scanning_tool.gui.tk.sections.ollama.ensure_model_installed",
        lambda model, exit_on_error=False: True,
    )

    def fake_log_model_running_status(model: str | None = None) -> bool:
        publish_ollama_status(
            f"Ollama model {model} is currently running.",
            model=model,
            ready=True,
        )
        return True

    monkeypatch.setattr(
        "scanning_tool.gui.tk.sections.ollama.log_model_running_status",
        fake_log_model_running_status,
    )

    success, message = OllamaModelManager.apply_model("dummy-model")

    assert success is True
    assert "dummy-model" in message
    assert any(event.get("model") == "dummy-model" for event in received)

    ollama_status_updated.disconnect(on_status)
