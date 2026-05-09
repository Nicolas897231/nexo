import logging
import time
import uuid
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")
logger = logging.getLogger("nexovia.request")


def get_request_id() -> str:
    return request_id_ctx.get() or str(uuid.uuid4())


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        try:
            uuid.UUID(request_id)
        except ValueError:
            request_id = str(uuid.uuid4())
        token = request_id_ctx.set(request_id)
        start = time.perf_counter()
        try:
            response = await call_next(request)
            return response
        finally:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.info(
                "request completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": locals().get("response").status_code
                    if "response" in locals()
                    else 500,
                    "duration_ms": duration_ms,
                },
            )
            if "response" in locals():
                response.headers["X-Request-ID"] = request_id
            request_id_ctx.reset(token)
