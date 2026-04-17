# Decision 1: Separate configuration models from domain models

**Why:** The domain layer should represent business concepts, not application settings.

**What changed:** Configuration DTOs were moved from `domain/models.py` into `config/models.py`.

**Result:** `domain` now contains only deposit, scan signature, capture, and overlay models.
