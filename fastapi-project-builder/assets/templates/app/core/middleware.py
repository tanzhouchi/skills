"""
请求追踪中间件。

使用纯 ASGI 实现，避免 BaseHTTPMiddleware 对异常传播和流式响应的影响。
"""

from time import perf_counter
from uuid import uuid4

from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.logger import get_business_logger

REQUEST_ID_HEADER = "x-request-id"
PROCESS_TIME_HEADER = "x-process-time"


class RequestIDMiddleware:
    """为每个 HTTP 请求注入请求编号和耗时响应头。"""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app
        self.logger = get_business_logger()

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        request_id = headers.get(REQUEST_ID_HEADER) or str(uuid4())
        start_time = perf_counter()
        method = scope.get("method", "-")
        path = scope.get("path", "-")

        self.logger.info("请求开始: request_id=%s method=%s path=%s", request_id, method, path)

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                process_time = perf_counter() - start_time
                response_headers = MutableHeaders(scope=message)
                response_headers[REQUEST_ID_HEADER] = request_id
                response_headers[PROCESS_TIME_HEADER] = f"{process_time:.6f}"
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception:
            self.logger.exception(
                "请求异常: request_id=%s method=%s path=%s",
                request_id,
                method,
                path,
            )
            raise
        finally:
            process_time = perf_counter() - start_time
            self.logger.info(
                "请求结束: request_id=%s method=%s path=%s process_time=%.6f",
                request_id,
                method,
                path,
                process_time,
            )
