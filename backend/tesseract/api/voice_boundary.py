"""Bound and authorize live uploads before the multipart parser spools any bytes."""

from fastapi import HTTPException, Request
from starlette.responses import JSONResponse


class VoiceBoundary:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or not scope["path"].startswith("/api/voice/"):
            return await self.app(scope, receive, send)
        from tesseract.api.routers.voice import MAX_UPLOAD, authorize

        limit = MAX_UPLOAD + 64 * 1024  # audio plus bounded form metadata/headers
        try:
            request = Request(scope)
            authorize(request)
            length = request.headers.get("content-length")
            if length is not None and (not length.isdigit() or int(length) > limit):
                raise HTTPException(413, "recording request too large")
        except HTTPException as error:
            return await JSONResponse({"detail": error.detail}, status_code=error.status_code)(
                scope, receive, send
            )
        size = 0

        async def bounded_receive():
            nonlocal size
            message = await receive()
            size += len(message.get("body", b""))
            if size > limit:
                raise HTTPException(413, "recording request too large")
            return message

        await self.app(scope, bounded_receive, send)
