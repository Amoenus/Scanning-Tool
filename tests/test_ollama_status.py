from scanning_tool.ollama.status import publish_ollama_status
from scanning_tool.state.signals.runtime import ollama_readiness_changed, ollama_status_updated


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

