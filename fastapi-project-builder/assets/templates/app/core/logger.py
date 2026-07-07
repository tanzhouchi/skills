"""
日志系统配置模块。

采用 logging.config.dictConfig 声明式配置，将 formatters/handlers/loggers
三要素集中管理。INFO/WARNING 写入正常日志文件，ERROR/CRITICAL 写入错误日志文件，
两类日志均按日期自动切割，互不干扰。日志路径从 config/config.yaml 读取。

架构说明：
- 定义独立业务 logger "__PROJECT_SLUG__"（propagate=False），应用代码通过
  get_business_logger() 获取，防止日志污染 root logger
- uvicorn 的 access/error/asgi logger 直接纳入本项目 handler 体系，
  不再依赖 root 传播
- init_log() 支持双重调用（模块级 + lifespan），通过 _initialized 标记保证幂等
"""

import logging
import logging.config
import logging.handlers
import os

from app.core.config import get_settings

# ---- 常量 ----
LOG_FORMAT = "%(asctime)s [%(levelname)s] [%(filename)s] [%(funcName)s:%(lineno)d] - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
BUSINESS_LOGGER_NAME = "__PROJECT_SLUG__"
PROJECT_NAME = "__PROJECT_SLUG__"

_initialized = False


class ErrorOnlyFilter(logging.Filter):
    """只允许 ERROR 及以上级别通过，用于错误日志文件。"""

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno >= logging.ERROR


class BelowErrorFilter(logging.Filter):
    """只允许 ERROR 以下级别通过，用于正常访问日志文件。"""

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno < logging.ERROR


def _resolve_log_dir() -> str:
    """解析日志目录绝对路径。"""
    settings = get_settings()
    log_dir = settings.log.path
    if not os.path.isabs(log_dir):
        # 相对路径：相对于项目根目录（从 app/core/logger.py 向上 3 级）
        log_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            log_dir,
        )
    os.makedirs(log_dir, exist_ok=True)
    return log_dir


def _build_log_config(log_dir: str, console_enabled: bool) -> dict:
    """
    构建 dictConfig 所需的配置字典。

    Args:
        log_dir: 日志文件目录
        console_enabled: 是否启用控制台输出

    Returns:
        dict: logging.config.dictConfig 可用的配置字典
    """
    level = "DEBUG"

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": LOG_FORMAT,
                "datefmt": DATE_FORMAT,
            },
        },
        "filters": {
            "below_error": {
                "()": "app.core.logger.BelowErrorFilter",
            },
            "error_only": {
                "()": "app.core.logger.ErrorOnlyFilter",
            },
        },
        "handlers": {
            "access_file": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "level": "DEBUG",
                "formatter": "verbose",
                "filename": os.path.join(log_dir, f"{PROJECT_NAME}.log"),
                "when": "midnight",
                "interval": 1,
                "backupCount": 30,
                "encoding": "utf-8",
                "filters": ["below_error"],
            },
            "error_file": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "level": "ERROR",
                "formatter": "verbose",
                "filename": os.path.join(log_dir, f"{PROJECT_NAME}-error.log"),
                "when": "midnight",
                "interval": 1,
                "backupCount": 30,
                "encoding": "utf-8",
                "filters": ["error_only"],
            },
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "verbose",
            },
        },
        "loggers": {
            # 独立业务 logger — 应用代码统一入口，不依赖 root
            BUSINESS_LOGGER_NAME: {
                "handlers": (
                    ["access_file", "error_file", "console"]
                    if console_enabled else ["access_file", "error_file"]
                ),
                "level": level,
                "propagate": False,
            },
            # 接管 uvicorn 日志 — 直接挂载本项目 handler，清空 uvicorn 自带 handler
            "uvicorn.access": {
                "handlers": (
                    ["access_file", "error_file", "console"]
                    if console_enabled else ["access_file", "error_file"]
                ),
                "level": level,
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": (
                    ["access_file", "error_file", "console"]
                    if console_enabled else ["access_file", "error_file"]
                ),
                "level": level,
                "propagate": False,
            },
            "uvicorn.asgi": {
                "handlers": (
                    ["access_file", "error_file", "console"]
                    if console_enabled else ["access_file", "error_file"]
                ),
                "level": level,
                "propagate": False,
            },
        },
        "root": {
            "handlers": (
                ["access_file", "error_file", "console"]
                if console_enabled else ["access_file", "error_file"]
            ),
            "level": level,
        },
    }


def _fix_handler_suffixes(log_dir: str) -> None:
    """
    修正 TimedRotatingFileHandler 的切割文件后缀格式。

    dictConfig 无法直接设置 handler 的 suffix 属性，
    因此在 dictConfig 之后手动修正。

    Args:
        log_dir: 日志文件目录
    """
    access_path = os.path.join(log_dir, f"{PROJECT_NAME}.log")
    error_path = os.path.join(log_dir, f"{PROJECT_NAME}-error.log")

    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        if isinstance(handler, logging.handlers.TimedRotatingFileHandler):
            if handler.baseFilename == os.path.abspath(access_path):
                handler.suffix = "%Y-%m-%d"
            elif handler.baseFilename == os.path.abspath(error_path):
                handler.suffix = "%Y-%m-%d"


def init_log() -> None:
    """
    初始化日志系统（幂等 — 多次调用只生效一次）。

    采用 dictConfig 声明式配置，确保：
    - 双文件分离（正常日志 + 错误日志）
    - 独立业务 logger "__PROJECT_SLUG__"
    - uvicorn 日志完全纳入本项目 handler 体系
    - 模块级调用（main.py）+ lifespan 调用双重保护

    模块导入阶段首次调用可捕获 create_app 等早期日志，
    lifespan 中二次调用因 _initialized 标记直接跳过。
    """
    global _initialized
    if _initialized:
        return

    settings = get_settings()
    log_dir = _resolve_log_dir()
    config = _build_log_config(log_dir, console_enabled=settings.log.console)

    logging.config.dictConfig(config)
    _fix_handler_suffixes(log_dir)

    _initialized = True


def get_business_logger() -> logging.Logger:
    """
    返回业务 logger 实例。

    应用代码应通过此函数获取统一的 logger，而非直接使用
    logging.getLogger(__name__)，确保所有业务日志集中在
    "__PROJECT_SLUG__" 命名空间下。

    Returns:
        logging.Logger: 名为 "__PROJECT_SLUG__" 的 logger
    """
    return logging.getLogger(BUSINESS_LOGGER_NAME)
