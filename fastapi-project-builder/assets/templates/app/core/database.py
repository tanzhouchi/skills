"""
数据库引擎与会话依赖。

模块级唯一引擎由统一配置创建，业务代码只能通过 get_db()
获取请求级 Session，禁止在业务层自行创建引擎。
"""

from collections.abc import Generator
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


def _build_engine_kwargs() -> dict[str, Any]:
    """根据连接类型构造引擎参数。"""
    settings = get_settings()
    database_url = settings.database.sqlalchemy_url
    if database_url.startswith("sqlite"):
        return {
            "connect_args": {"check_same_thread": False},
            "echo": settings.database.echo,
            "future": True,
        }
    return {
        "pool_pre_ping": True,
        "pool_size": settings.database.pool_size,
        "max_overflow": settings.database.max_overflow,
        "pool_timeout": settings.database.pool_timeout,
        "pool_recycle": settings.database.pool_recycle,
        "echo": settings.database.echo,
        "future": True,
    }


def create_database_engine() -> Engine:
    """创建 SQLAlchemy 引擎。"""
    settings = get_settings()
    return create_engine(settings.database.sqlalchemy_url, **_build_engine_kwargs())


engine = create_database_engine()

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    future=True,
)


def get_db() -> Generator[Session, None, None]:
    """提供请求级数据库会话。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
