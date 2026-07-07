"""
统一响应格式模块。

所有 API 响应都通过此模块的辅助函数构建，确保格式一致。

成功响应：{"code": 200, "data": ..., "message": "请求成功", "timestamp": "..."}
分页响应：{"code": 200, "data": {"total": N, "page": N, "page_size": N, "total_pages": N, "items": [...]}, ...}
错误响应：{"code": 400, "data": null, "message": "错误消息", "timestamp": "..."}
"""

from collections.abc import Mapping
from datetime import datetime
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field

from app.common.datetime import format_response_datetime, local_now_str

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    """统一成功响应模型。"""

    code: int = Field(200, description="HTTP 状态码")
    data: T = Field(..., description="响应数据")
    message: Optional[str] = Field(None, description="提示消息")
    timestamp: str = Field(default_factory=local_now_str, description="响应时间戳")


class PaginatedData(BaseModel, Generic[T]):
    """分页数据模型。"""

    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页记录数")
    total_pages: int = Field(..., description="总页数")
    items: list[T] = Field(..., description="数据列表")


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应模型。"""

    code: int = Field(200, description="HTTP 状态码")
    data: PaginatedData[T] = Field(..., description="分页数据")
    message: Optional[str] = Field(None, description="提示消息")
    timestamp: str = Field(default_factory=local_now_str, description="响应时间戳")


class ErrorResponse(BaseModel):
    """统一错误响应模型。"""

    code: int = Field(..., description="HTTP 状态码")
    data: Optional[Any] = Field(None, description="错误详情数据")
    message: str = Field(..., description="错误消息")
    timestamp: str = Field(default_factory=local_now_str, description="响应时间戳")


def _serialize_response_data(data: Any) -> Any:
    """递归规范化统一响应中的业务数据，避免各接口重复处理时间格式。"""
    if isinstance(data, datetime):
        return format_response_datetime(data)
    if isinstance(data, BaseModel):
        return _serialize_response_data(data.model_dump())
    if isinstance(data, Mapping):
        return {key: _serialize_response_data(value) for key, value in data.items()}
    if isinstance(data, list | tuple):
        return [_serialize_response_data(item) for item in data]
    return data


def success_response(data: Any = None, message: str = "请求成功") -> SuccessResponse:
    """构建成功响应（200）。"""
    return SuccessResponse(code=200, data=_serialize_response_data(data), message=message)


def paginated_response(
    items: list[Any],
    total: int,
    page: int,
    page_size: int,
    message: str = "请求成功",
) -> PaginatedResponse:
    """构建分页成功响应。"""
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return PaginatedResponse(
        code=200,
        data=PaginatedData(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            items=_serialize_response_data(items),
        ),
        message=message,
    )


def error_response(code: int, message: str, detail: Any = None) -> ErrorResponse:
    """
    构建错误响应。

    detail 参数用于传递错误详情：
    - 传入 list 时包装为 {"errors": [...]}
    - 传入其他值时包装为 {"errors": [detail]}
    """
    error_data = None
    if detail is not None:
        if isinstance(detail, list):
            error_data = {"errors": detail}
        else:
            error_data = {"errors": [detail]}
    return ErrorResponse(code=code, data=error_data, message=message)


def created_response(data: Any = None, message: str = "创建成功") -> SuccessResponse:
    """构建资源创建成功响应（201）。"""
    return SuccessResponse(code=201, data=_serialize_response_data(data), message=message)


def updated_response(data: Any = None, message: str = "更新成功") -> SuccessResponse:
    """构建资源更新成功响应。"""
    return SuccessResponse(code=200, data=_serialize_response_data(data), message=message)


def deleted_response(message: str = "删除成功") -> SuccessResponse:
    """构建资源删除成功响应。"""
    return SuccessResponse(code=200, data=None, message=message)


# ---- OpenAPI 响应示例辅助工具 ----

def _make_success_example(data_example: dict[str, Any], message: str = "请求成功") -> dict[str, Any]:
    """内部：按统一成功响应格式包装 data 示例值。"""
    return {
        "code": 200,
        "data": data_example,
        "message": message,
        "timestamp": "2026-07-01 12:00:00",
    }


def _make_paginated_example(
    items_example: list[dict[str, Any]],
    total: int = 100,
    page: int = 1,
    page_size: int = 20,
    message: str = "请求成功",
) -> dict[str, Any]:
    """内部：按统一分页响应格式包装 items 示例值。"""
    return {
        "code": 200,
        "data": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": 5,
            "items": items_example,
        },
        "message": message,
        "timestamp": "2026-07-01 12:00:00",
    }


def openapi_success_example(
    data_example: dict[str, Any],
    message: str = "请求成功",
) -> dict[int | str, dict[str, Any]]:
    """
    生成 OpenAPI 成功响应示例（用于路由 decorator 的 responses 参数）。

    用法：
        @router.get("", responses=openapi_success_example({...}))
    """
    return {
        200: {
            "description": "请求成功",
            "content": {
                "application/json": {
                    "example": _make_success_example(data_example, message),
                },
            },
        },
    }


def openapi_paginated_example(
    items_example: list[dict[str, Any]],
    total: int = 100,
    page: int = 1,
    page_size: int = 20,
    message: str = "请求成功",
) -> dict[int | str, dict[str, Any]]:
    """
    生成 OpenAPI 分页响应示例（用于路由 decorator 的 responses 参数）。

    用法：
        @router.get("", responses=openapi_paginated_example([{...}]))
    """
    return {
        200: {
            "description": "请求成功",
            "content": {
                "application/json": {
                    "example": _make_paginated_example(
                        items_example, total, page, page_size, message,
                    ),
                },
            },
        },
    }
