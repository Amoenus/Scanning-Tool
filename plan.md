1. **Analyze the `EditModeService` in `src/scanning_tool/services/edit_mode_service.py`:**
   - The class currently uses dictionaries extensively to pass payload data for regions: `payload: dict[str, object] | None`.
   - It also manually parses these unstructured payloads with methods like `_coerce_int_payload` and `_normalize_payload`.
   - It directly creates region dictionaries with raw string keys like `{"left": left, "top": top, ...}` in `_payload_for_region`.

2. **Introduce Strongly-Typed DTOs in `src/scanning_tool/gui/dtos.py`:**
   - We already have `RegionUpdatePayload` and `OffsetUpdatePayload`.
   - We need new models for the edit mode payloads: `RegionSelectPayload` and `RegionDragPayload` (or similar) that encapsulate `delta_left`, `delta_top`, `delta_x`, `delta_y`, etc.
   - Alternatively, we can use a dedicated `EditModePayload` in `src/scanning_tool/gui/dtos.py`.

3. **Refactor `EditModeService` to use Pydantic models:**
   - Add new DTOs to `src/scanning_tool/gui/dtos.py`:
     - `RegionSelectPayload(BaseModel)`: `region: str | None = None`
     - `RegionDragPayload(BaseModel)`: `left: int | None = None`, `top: int | None = None`, `width: int | None = None`, `height: int | None = None`, `delta_left: int = 0`, `delta_top: int = 0`, `delta_width: int = 0`, `delta_height: int = 0`, `x: int | None = None`, `y: int | None = None`, `delta_x: int = 0`, `delta_y: int = 0`.
   - Update `EditModeService` methods `_on_drag_region`, `_on_nudge_region`, `_on_select_region` to accept and validate the new DTOs using `.model_validate(payload)`.
   - Remove redundant `_coerce_int_payload` and `_normalize_payload` methods from `EditModeService` as validation will be handled by Pydantic.

4. **Verify tests pass:**
   - Run the test suite using `uv run --managed-python --with-requirements requirements-dev.txt -- pytest tests/`.
   - Ensure `uv run --managed-python --with-requirements requirements-dev.txt -- mypy src/` and `uv run --managed-python --with-requirements requirements-dev.txt -- ruff check src/` pass.

5. **Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.**

6. **Submit PR:**
   - Title: `🪛 Chisel: [Structural improvement]`
   - Description following the specified Chisel format.
