"""
测试夹具。

每个测试使用独立应用实例、独立数据库连接和连接级事务回滚，
避免测试之间互相污染。
"""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


@pytest.fixture()
def db_session(tmp_path, monkeypatch) -> Generator[Session, None, None]:
    """提供连接级事务隔离的数据库会话。"""
    database_url = f"sqlite+pysqlite:///{tmp_path / 'test.db'}"
    monkeypatch.setenv("DATABASE_URL", database_url)

    from app.core.config import get_settings

    get_settings.cache_clear()

    from app.core import database as database_module

    test_engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        future=True,
    )
    connection = test_engine.connect()
    transaction = connection.begin()
    testing_session_local = sessionmaker(
        bind=connection,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        future=True,
        join_transaction_mode="create_savepoint",
    )

    monkeypatch.setattr(database_module, "engine", test_engine)
    monkeypatch.setattr(database_module, "SessionLocal", testing_session_local)

    session = testing_session_local()
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
        test_engine.dispose()
        get_settings.cache_clear()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """提供独立 FastAPI 应用测试客户端。"""
    from app.core import database as database_module
    from app.main import create_app

    app = create_app()

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[database_module.get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
