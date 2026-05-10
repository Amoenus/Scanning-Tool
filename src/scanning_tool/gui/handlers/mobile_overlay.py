from __future__ import annotations

import io
import logging
import webbrowser
from typing import TYPE_CHECKING

from scanning_tool.state.actions import ConfigAction
from scanning_tool.state.signals import mobile_qr_ready, status_updated

if TYPE_CHECKING:
    from scanning_tool.gui.context import ActionContext
    from scanning_tool.gui.handlers import Handler


def _handle_open_mobile_ui(
    payload: dict[str, object],
    context: ActionContext,
) -> None:
    url = str(payload["url"])
    try:
        webbrowser.open_new_tab(url)
        status_updated.send(None, message=f"Opening overlay in browser: {url}")
    except Exception as exc:
        status_updated.send(None, message=f"Unable to open browser: {exc}")


def _handle_show_mobile_qr(
    payload: dict[str, object],
    context: ActionContext,
) -> None:
    url = str(payload.get("url", ""))
    if not url:
        status_updated.send(None, message="Unable to generate mobile QR code: missing URL.")
        return

    try:
        import segno

        qr = segno.make(url, error="h")
        with io.BytesIO() as buffer:
            qr.save(buffer, kind="png", scale=8, border=2)
            png_bytes = buffer.getvalue()
    except Exception as exc:
        status_updated.send(None, message=f"Unable to generate QR code: {exc}")
        logging.exception("Failed to generate mobile QR code for %s: %s", url, exc)
        return

    mobile_qr_ready.send(None, url=url, png_bytes=png_bytes)
    status_updated.send(None, message="Mobile overlay QR code generated.")


MOBILE_OVERLAY_ACTION_HANDLERS: dict[object, Handler] = {
    ConfigAction.OPEN_MOBILE_UI: _handle_open_mobile_ui,
    ConfigAction.SHOW_MOBILE_QR: _handle_show_mobile_qr,
}
