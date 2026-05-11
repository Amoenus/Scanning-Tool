import cv2
import numpy as np

from scanning_tool.core.anchor import AnchorRegionTracker
from scanning_tool.domain.models import CaptureRegion


class DummyCaptureProvider:
    def capture(self, region):
        from PIL import Image

        return Image.new("RGB", (100, 100))


def test_load_templates_reads_supported_images(tmp_path):
    image_path = tmp_path / "template.png"
    image = np.zeros((16, 16, 3), dtype=np.uint8)
    cv2.imwrite(str(image_path), image)

    tracker = AnchorRegionTracker(str(tmp_path), capture_provider=DummyCaptureProvider(), threshold=0.5)

    assert tracker.last_loaded_count == 1
    assert tracker.templates[0].name == "template.png"


def test_capture_region_to_mss_monitor_and_tuple_conversion():
    region = CaptureRegion(left=10, top=20, width=100, height=50)

    assert region.to_mss_monitor() == {
        "left": 10,
        "top": 20,
        "width": 100,
        "height": 50,
    }
    assert region.to_monitor() == {
        "left": 10,
        "top": 20,
        "width": 100,
        "height": 50,
    }
    assert region.to_tuple() == (10, 20, 100, 50)


def test_load_templates_returns_zero_for_empty_directory(tmp_path):
    tracker = AnchorRegionTracker(str(tmp_path), capture_provider=DummyCaptureProvider(), threshold=0.5)

    assert tracker.last_loaded_count == 0
    assert tracker.templates == []
