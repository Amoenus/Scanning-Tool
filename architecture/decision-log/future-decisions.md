# Future decisions to capture

- Split `domain/models.py` into smaller domain modules such as `ore.py`, `scan_signature.py`, `capture.py`, and `overlay.py`.
- Evaluate moving the web overlay into a dedicated `web_service.py` module.
- Add a dedicated `services/state_service.py` or similar for explicit service lifecycle management.
- Define a clear boundary between GUI state and service runtime state to reduce coupling.
