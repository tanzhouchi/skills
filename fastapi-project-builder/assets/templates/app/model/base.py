"""
SQLAlchemy 模型基类。
"""

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """所有 ORM 模型的统一基类。"""


class IdMixin:
    """整数主键字段混入。"""

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="主键编号")


class TimestampMixin:
    """创建时间和更新时间字段混入。"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新时间",
    )
