"""OCR via Ollama vision models."""

import io
from loguru import logger
from typing import Optional
import ollama

from PIL import Image

from scanning_tool.ollama import get_ollama_client, get_ollama_model
from scanning_tool.domain.models import ModelPromptProfile


_DEFAULT_PROMPT = "Extract the numeric code shown in this image. Only return the code, no extra words."

_MODEL_PROMPTS: tuple[ModelPromptProfile, ...] = (
    ModelPromptProfile(
        prefix="moondream",
        prompt=(
            "Only output the numbers you see in this image. Do not describe the image. "
            "If there are no numbers, output nothing."
        ),
    ),
    ModelPromptProfile(prefix="granite", prompt="Read all numbers in this image. Only return the numbers."),
    ModelPromptProfile(prefix="deepseek-ocr", prompt="Read all text in this image. Only return the numbers."),
    ModelPromptProfile(
        prefix="smolvlm",
        prompt="Only output the numbers you see in this image. Do not describe the image. If there are no numbers, output nothing.",
    ),
    ModelPromptProfile(prefix="bakllava", prompt="Extract all numbers from this image. Only output the numbers."),
    ModelPromptProfile(prefix="llava", prompt="What numbers are visible in this image? Only output the numbers."),
    ModelPromptProfile(prefix="qwen2.5vl", prompt="Extract all numbers from this image. Only output the numbers."),
)


def _select_prompt(model: Optional[str]) -> str:
    if not model:
        return _DEFAULT_PROMPT
    name = model.lower()
    for profile in _MODEL_PROMPTS:
        if name.startswith(profile.prefix):
            return profile.prompt
    return _DEFAULT_PROMPT


def ocr_with_ollama(pil_img: Image.Image, model: Optional[str] = None) -> str:
    """Send an image to Ollama for OCR and return the extracted text."""
    if model is None:
        model = get_ollama_model()
    buf = io.BytesIO()
    pil_img.save(buf, format="PNG")
    img_bytes = buf.getvalue()
    client: ollama.Client = get_ollama_client()
    prompt = _select_prompt(model)
    logger.debug(f"Using OCR prompt for model '{model}': {prompt}")
    try:
        response: ollama.ChatResponse = client.chat(
            model=model,
            messages=[{
                "role": "user",
                "content": prompt,
                "images": [img_bytes],
            }],
        )
        return response["message"]["content"].strip()
    except Exception as e:
        logger.error(f"Ollama OCR error: {e}")
        return ""
