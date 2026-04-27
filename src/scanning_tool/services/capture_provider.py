from __future__ import annotations

import numpy as np
from loguru import logger
from mss import mss
from mss.base import MSS
from mss.screenshot import ScreenShot
from PIL import Image as PILModule
from PIL.Image import Image

from scanning_tool.interfaces.capture import CaptureProvider


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scanning_tool.domain.alignment import CaptureRegion
class ScreenCaptureProvider(CaptureProvider):
    """Capture a PIL image from a screen region."""

    def capture(self, region: CaptureRegion) -> Image:
        # Using 'mss' as a context manager automatically handles cleanup
        sct: MSS = mss()
        with sct:
            try:    # The 'grab' method returns a ScreenShot object
                screenshot: ScreenShot = sct.grab(region.to_monitor())
            except Exception as exc:
                logger.error(f"Screen capture failed: {exc}")
                raise RuntimeError("Screen capture failed") from exc

            width, height = screenshot.size
            frame = np.frombuffer(screenshot.rgb, dtype=np.uint8)
            frame = frame.reshape((height, width, 3))
            return PILModule.fromarray(frame, "RGB")
