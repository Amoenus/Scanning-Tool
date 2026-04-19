from __future__ import annotations

import mss
from PIL import Image

from scanning_tool.domain.alignment import CaptureRegion
from scanning_tool.interfaces.capture import CaptureProvider


class ScreenCaptureProvider(CaptureProvider):
    """Capture a PIL image from a screen region."""

    def capture(self, region: CaptureRegion) -> Image.Image:
        with mss.mss() as sct:
            img = sct.grab(region.to_monitor())
            return Image.frombytes("RGB", img.size, img.rgb)
