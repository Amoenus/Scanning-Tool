from types import SimpleNamespace
from unittest.mock import patch

from PIL import Image

from scanning_tool.services.ocr_service import (
    OllamaChatMessage,
    _build_ollama_messages,
    _send_ollama_chat,
    ocr_with_ollama,
)


def test_build_ollama_messages_returns_typed_message_payload() -> None:
    messages = _build_ollama_messages("test prompt", b"dummy-bytes")

    assert len(messages) == 1
    assert messages[0] == OllamaChatMessage(
        role="user",
        content="test prompt",
        images=[b"dummy-bytes"],
    )
    assert messages[0].to_payload() == {
        "role": "user",
        "content": "test prompt",
        "images": [b"dummy-bytes"],
    }


def test_send_ollama_chat_invokes_client_with_payload() -> None:
    fake_response = SimpleNamespace(message=SimpleNamespace(content="1234"))

    class FakeClient:
        def __init__(self) -> None:
            self.chat_called = False
            self.chat_args: tuple[str, list[dict[str, object]]] | None = None

        def chat(
            self, model: str, messages: list[dict[str, object]],
        ) -> SimpleNamespace:
            self.chat_called = True
            self.chat_args = (model, messages)
            return fake_response

    fake_client = FakeClient()

    with patch(
        "scanning_tool.services.ocr_service.get_ollama_client", return_value=fake_client,
    ):
        result = _send_ollama_chat("dummy-model", "some prompt", b"dummy-bytes")

    assert result == "1234"
    assert fake_client.chat_called is True
    assert fake_client.chat_args is not None
    assert fake_client.chat_args[0] == "dummy-model"
    assert fake_client.chat_args[1] == [
        {
            "role": "user",
            "content": "some prompt",
            "images": [b"dummy-bytes"],
        },
    ]


def test_ocr_with_ollama_returns_empty_when_model_is_not_configured(monkeypatch):
    monkeypatch.setattr(
        "scanning_tool.services.ocr_service.get_ollama_model", lambda: "",
    )
    result = ocr_with_ollama(Image.new("RGB", (1, 1)), model=None)

    assert result == ""
