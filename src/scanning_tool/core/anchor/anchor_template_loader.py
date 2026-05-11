from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import cv2
from loguru import logger

from scanning_tool.config import ensure_anchor_directory

if TYPE_CHECKING:
    import numpy as np


@dataclass(frozen=True)
class AnchorTemplate:
    """Represents a named anchor image template."""

    name: str
    image: np.ndarray


class AnchorTemplateLoader:
    """Load anchor templates from disk."""

    SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp"}

    def __init__(self, template_dir: str) -> None:
        self.template_dir = template_dir
        self.templates: list[AnchorTemplate] = []
        self.last_loaded_count = 0
        self.load_templates()

    def set_directory(self, template_dir: str) -> int:
        self.template_dir = template_dir
        return self.load_templates()

    def load_templates(self) -> int:
        ensure_anchor_directory(self.template_dir)
        directory = Path(self.template_dir)
        if not directory.exists():
            logger.debug(f"Anchor template directory does not exist: {directory}")
            self.templates = []
            self.last_loaded_count = 0
            return 0

        self.templates = self._load_image_files(directory)
        self.last_loaded_count = len(self.templates)
        self._log_template_load_result(directory)
        return self.last_loaded_count

    def _load_image_files(self, directory: Path) -> list[AnchorTemplate]:
        loaded: list[AnchorTemplate] = []
        for path in sorted(directory.glob("**/*")):
            if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS or not path.is_file():
                continue
            image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
            if image is None:
                logger.warning(f"Failed to load anchor template: {path}")
                continue
            loaded.append(AnchorTemplate(name=path.name, image=image))
        return loaded

    def _log_template_load_result(self, directory: Path) -> None:
        if self.last_loaded_count == 0:
            logger.warning(
                "No anchor templates were loaded. Head sway compensation will remain disabled until templates are added.",
            )
        else:
            logger.info(
                f"Loaded {self.last_loaded_count} anchor templates from {directory}",
            )
