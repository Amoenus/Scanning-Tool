from __future__ import annotations

from PIL import Image

from scanning_tool.interfaces.capture import OCRProvider
from scanning_tool.services.ocr_service import ocr_with_ollama


class OllamaOCRProvider(OCRProvider):
    """OCR adapter that delegates to the Ollama service."""

    def extract_text(self, pil_img: Image.Image) -> str:
        """Extract text from an image using Ollama OCR service.

        Parameters
        ----------
        pil_img : Image.Image
            The PIL image to extract text from.

        Returns
        -------
        str
            The extracted text from the image.

        """
        return ocr_with_ollama(pil_img)
