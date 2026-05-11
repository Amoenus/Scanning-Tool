"""OCR service abstraction for Ollama vision models."""

import io
from dataclasses import dataclass

import ollama
from loguru import logger
from PIL import Image

from scanning_tool.ollama import get_ollama_client, get_ollama_model


@dataclass(frozen=True)
class ModelPromptProfile:
    """Profile for model-specific OCR prompts.

    Attributes
    ----------
    prefix : str
        The model name prefix to match against.
    prompt : str
        The OCR prompt to use for this model.

    """

    prefix: str
    prompt: str


@dataclass(frozen=True)
class OllamaChatMessage:
    role: str
    content: str
    images: list[bytes]

    def to_payload(self) -> dict[str, object]:
        return {
            "role": self.role,
            "content": self.content,
            "images": self.images,
        }


_DEFAULT_PROMPT = "Extract the numeric code shown in this image. Only return the code, no extra words."

_MODEL_PROMPTS: tuple[ModelPromptProfile, ...] = (
    ModelPromptProfile(
        prefix="moondream",
        prompt=(
            "Only output the numbers you see in this image. Do not describe the image. "
            "If there are no numbers, output nothing."
        ),
    ),
    ModelPromptProfile(
        prefix="granite",
        prompt="Read all numbers in this image. Only return the numbers.",
    ),
    ModelPromptProfile(
        prefix="deepseek-ocr",
        prompt="Read all text in this image. Only return the numbers.",
    ),
    ModelPromptProfile(
        prefix="smolvlm",
        prompt="Only output the numbers you see in this image. Do not describe the image. If there are no numbers, output nothing.",
    ),
    ModelPromptProfile(
        prefix="bakllava",
        prompt="Extract all numbers from this image. Only output the numbers.",
    ),
    ModelPromptProfile(
        prefix="llava",
        prompt="What numbers are visible in this image? Only output the numbers.",
    ),
    ModelPromptProfile(
        prefix="qwen2.5vl",
        prompt="Extract all numbers from this image. Only output the numbers.",
    ),
)


def _select_prompt(model: str | None) -> str:
    if not model:
        return _DEFAULT_PROMPT
    name = model.lower()
    for profile in _MODEL_PROMPTS:
        if name.startswith(profile.prefix):
            return profile.prompt
    return _DEFAULT_PROMPT


def _get_image_bytes(pil_img: Image.Image) -> bytes:
    buf = io.BytesIO()
    pil_img.save(buf, format="PNG")
    return buf.getvalue()


def _build_ollama_messages(prompt: str, image_bytes: bytes) -> list[OllamaChatMessage]:
    return [OllamaChatMessage(role="user", content=prompt, images=[image_bytes])]


def _send_ollama_chat(model: str, prompt: str, image_bytes: bytes) -> str:
    client: ollama.Client = get_ollama_client()
    messages = [message.to_payload() for message in _build_ollama_messages(prompt, image_bytes)]
    response: ollama.ChatResponse = client.chat(model=model, messages=messages)
    content = response.message.content
    return content.strip() if content else ""


def ocr_with_ollama(pil_img: Image.Image, model: str | None = None) -> str:
    """Send an image to Ollama for OCR and return the extracted text."""
    if model is None:
        model = get_ollama_model()

    if not model:
        logger.error(
            "Ollama model is not configured. OCR cannot proceed until a model is set.",
        )
        return ""

    image_bytes = _get_image_bytes(pil_img)
    prompt = _select_prompt(model)
    logger.debug(f"Using OCR prompt for model '{model}': {prompt}")
    try:
        return _send_ollama_chat(model, prompt, image_bytes)
    except Exception as e:
        logger.error(f"Ollama OCR error: {e}")
        return ""
