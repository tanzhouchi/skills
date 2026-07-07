"""日期时间工具函数。"""

from datetime import datetime, timezone

from zoneinfo import ZoneInfo

# 项目默认时区：北京时间 (UTC+8)
_DEFAULT_TZ = ZoneInfo("Asia/Shanghai")


def utcnow() -> datetime:
    """返回当前 UTC 时间（timezone-aware）。"""
    return datetime.now(tz=timezone.utc)


def local_now() -> datetime:
    """返回当前北京时间（Asia/Shanghai, UTC+8）。"""
    return datetime.now(tz=_DEFAULT_TZ)


def local_now_str() -> str:
    """返回当前北京时间的格式化字符串（YYYY-MM-DD HH:MM:SS）。"""
    return local_now().strftime("%Y-%m-%d %H:%M:%S")


def format_response_datetime(value: datetime) -> str:
    """将接口响应中的时间统一转换为北京时间字符串。"""
    if value.tzinfo is None or value.utcoffset() is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(_DEFAULT_TZ).strftime("%Y-%m-%d %H:%M:%S")


def iso_now() -> str:
    """返回当前 UTC 时间的 ISO 8601 字符串。"""
    return utcnow().isoformat()
