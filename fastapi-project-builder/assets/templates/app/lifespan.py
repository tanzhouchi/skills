"""
应用生命周期管理。
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from importlib import import_module

from fastapi import FastAPI

from app.core.logger import get_business_logger, init_log


def _dispose_database_engine() -> None:
    """数据库模块存在时释放引擎，轻量项目无数据库时跳过。"""
    try:
        database_module = import_module("app.core.database")
    except ModuleNotFoundError as exc:
        if exc.name != "app.core.database":
            raise
        return
    engine = getattr(database_module, "engine", None)
    if engine is not None:
        engine.dispose()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """管理应用启动和关闭阶段的基础设施资源。"""
    init_log()
    logger = get_business_logger()
    logger.info("应用启动完成: %s", app.title)
    try:
        yield
    finally:
        _dispose_database_engine()
        logger.info("应用关闭完成: %s", app.title)
