"""
FastAPI 应用创建入口。

通过 create_app() 工厂函数创建应用实例，
便于测试时使用测试配置注入。
"""

import uvicorn
from fastapi import FastAPI

from app.api.v1.health_api import router as health_router
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exception_handlers import configure_exception_handlers
from app.core.logger import get_business_logger, init_log
from app.core.middleware import RequestIDMiddleware
from app.lifespan import lifespan

# ---- 模块级日志初始化 ----
# 在 create_app() 之前调用，确保模块导入阶段
# （如配置加载、数据库引擎创建）的日志也能被捕获。
# init_log() 内部有幂等保护，lifespan 中二次调用不会重复配置。
init_log()
_logger = get_business_logger()


def create_app() -> FastAPI:
    """创建并配置 FastAPI 应用实例。"""
    settings = get_settings()
    app = FastAPI(
        title=settings.app.name,
        description="__PROJECT_DESCRIPTION__",
        version=settings.app.version,
        debug=settings.app.debug,
        lifespan=lifespan,
    )

    # ---- 中间件注册 ----
    # Request ID 注入中间件：全链路追踪 + 请求耗时统计
    # 使用纯 ASGI 中间件，避免 BaseHTTPMiddleware 与 Starlette 异常处理链冲突
    app.add_middleware(RequestIDMiddleware)

    # ---- 异常处理器注册 ----
    configure_exception_handlers(app)

    # ---- 路由注册 ----
    # 健康检查不加前缀，直接在根路径可用
    app.include_router(health_router)
    # 业务 API 加 /api/v1 前缀
    app.include_router(api_router, prefix=settings.app.api_prefix)

    # 不在此处打 INFO 日志 — create_app() 是纯工厂函数，
    # 会被模块级、uvicorn 导入、reload 子进程等多处调用，
    # 启动完成的标志性日志统一在 lifespan 中输出。

    return app


app = create_app()


def main() -> None:
    """开发环境启动入口。"""
    settings = get_settings()
    _logger.info("启动开发服务器: %s:%d", settings.app.host, settings.app.port)
    uvicorn.run(
        "app.main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.debug,
        log_level="info",
    )


if __name__ == "__main__":
    main()
