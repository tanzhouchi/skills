"""
健康检查接口。

健康检查面向探针和网关，固定裸返回，不走统一响应包装。
"""

from fastapi import APIRouter

router = APIRouter(tags=["健康检查"])


@router.get("/health", summary="健康检查")
async def health() -> dict[str, str]:
    """返回服务存活状态。"""
    return {"status": "ok"}
