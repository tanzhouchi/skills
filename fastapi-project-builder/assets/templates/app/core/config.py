"""
配置读取模块。

加载顺序固定为 config.yaml -> config-local.yaml -> 环境变量。
DATABASE_URL 拥有最高优先级，DB_HOST/DB_PORT/DB_USER/DB_PASSWORD/DB_NAME
可分别覆盖数据库连接参数。
"""

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "config"


class AppConfig(BaseModel):
    """应用基础配置。"""

    name: str = "__PROJECT_DISPLAY_NAME__"
    version: str = "0.1.0"
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = 8000
    api_prefix: str = "/api/v1"


class DatabaseConfig(BaseModel):
    """数据库连接配置。"""

    host: str = "127.0.0.1"
    port: int = 5432
    user: str = "__PROJECT_SLUG_UNDERSCORE__"
    password: str = ""
    database: str = "__PROJECT_SLUG_UNDERSCORE__"
    pool_size: int = 20
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False
    url: str | None = Field(default=None, exclude=True)

    @property
    def sqlalchemy_url(self) -> str:
        """返回 SQLAlchemy 可用的连接地址。"""
        if self.url:
            return self.url
        auth = self.user
        if self.password:
            auth = f"{self.user}:{self.password}"
        return f"postgresql+psycopg://{auth}@{self.host}:{self.port}/{self.database}"


class RedisConfig(BaseModel):
    """Redis 配置。"""

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: str = ""
    max_connections: int = 50
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    broker_db: int = 7
    backend_url_db: int = 8


class LogConfig(BaseModel):
    """日志配置。"""

    console: bool = True
    path: str = "logs"


class Settings(BaseModel):
    """项目完整配置。"""

    app: AppConfig = Field(default_factory=AppConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    log: LogConfig = Field(default_factory=LogConfig)


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """递归合并配置，右侧优先。"""
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _read_yaml(path: Path) -> dict[str, Any]:
    """读取 YAML 配置文件，不存在时返回空配置。"""
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}
    if not isinstance(data, dict):
        raise ValueError(f"配置文件必须是对象结构: {path}")
    return data


def _apply_env_overrides(raw: dict[str, Any]) -> dict[str, Any]:
    """应用环境变量覆盖规则。"""
    import os

    database = dict(raw.get("database", {}))
    if os.getenv("DATABASE_URL"):
        database["url"] = os.environ["DATABASE_URL"]

    env_to_field = {
        "DB_HOST": "host",
        "DB_PORT": "port",
        "DB_USER": "user",
        "DB_PASSWORD": "password",
        "DB_NAME": "database",
    }
    for env_name, field_name in env_to_field.items():
        if os.getenv(env_name):
            value: str | int = os.environ[env_name]
            if field_name == "port":
                value = int(value)
            database[field_name] = value

    raw["database"] = database
    return raw


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """读取并缓存项目配置。"""
    base_config = _read_yaml(CONFIG_DIR / "config.yaml")
    local_config = _read_yaml(CONFIG_DIR / "config-local.yaml")
    raw_config = _deep_merge(base_config, local_config)
    return Settings.model_validate(_apply_env_overrides(raw_config))
