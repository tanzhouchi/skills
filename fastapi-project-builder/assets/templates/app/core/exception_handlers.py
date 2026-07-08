"""
全局异常处理器。

为 FastAPI 注册统一的 exception_handler，确保所有异常：
1. 被分类记录到日志（客户端错误 -> WARNING，服务端错误 -> ERROR）
2. 返回符合项目规范的 ErrorResponse 格式
3. 通用异常使用 logger.exception() 自动输出完整堆栈
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import AppBaseError
from app.core.logger import get_business_logger
from app.core.response import error_response

_logger = get_business_logger()


def configure_exception_handlers(app: FastAPI) -> None:
    """
    为 FastAPI 应用注册所有异常处理器。

    日志级别约定：
    - 客户端错误（4xx）-> logger.warning()
    - 服务端错误（5xx）-> logger.error()，通用异常加 exc_info=True 输出堆栈

    Args:
        app: FastAPI 应用实例
    """

    @app.exception_handler(AppBaseError)
    async def _handle_business_error(request: Request, exc: AppBaseError) -> JSONResponse:
        """处理业务异常及其子类（NotFound/Conflict/Forbidden/Validation）。"""
        level = logging.WARNING if exc.code < 500 else logging.ERROR
        _logger.log(level, "业务异常: [%s] %s %s -> %s",
                    exc.code, request.method, request.url, exc.message)
        return JSONResponse(
            status_code=exc.code,
            content=error_response(
                code=exc.code, message=exc.message
            ).model_dump(mode="json"),
        )

    @app.exception_handler(RequestValidationError)
    async def _handle_validation_error(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        """处理 FastAPI/Pydantic 请求参数校验失败（422）。"""
        _logger.warning("参数校验失败: %s %s -> %s",
                        request.method, request.url, exc.errors())
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response(
                code=422, message="请求参数校验失败", detail=exc.errors()
            ).model_dump(mode="json"),
        )

    @app.exception_handler(StarletteHTTPException)
    async def _handle_http_exception(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        """处理 Starlette/FastAPI 标准 HTTP 异常（404/405 等）。"""
        level = logging.WARNING if exc.status_code < 500 else logging.ERROR
        _logger.log(level, "HTTP 异常: [%d] %s %s -> %s",
                    exc.status_code, request.method, request.url, exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(
                code=exc.status_code, message=str(exc.detail)
            ).model_dump(mode="json"),
        )

    @app.exception_handler(Exception)
    async def _handle_general_exception(request: Request, exc: Exception) -> JSONResponse:
        """处理未捕获的通用异常（500），自动输出完整堆栈。"""
        _logger.error("未捕获的异常: %s %s -> %s",
                      request.method, request.url, exc, exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response(
                code=500, message="服务器内部错误"
            ).model_dump(mode="json"),
        )
