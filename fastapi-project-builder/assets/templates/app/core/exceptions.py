"""
业务异常定义。

所有业务异常继承自 AppBaseError，
FastAPI 统一 exception_handler 捕获后返回结构化错误响应。
"""


class AppBaseError(Exception):
    """业务异常基类。"""

    def __init__(self, message: str, code: int = 400) -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class NotFoundError(AppBaseError):
    """资源不存在。"""

    def __init__(self, message: str = "资源不存在") -> None:
        super().__init__(message, code=404)


class ConflictError(AppBaseError):
    """资源冲突（如重复创建）。"""

    def __init__(self, message: str = "资源冲突") -> None:
        super().__init__(message, code=409)


class ForbiddenError(AppBaseError):
    """无权限访问。"""

    def __init__(self, message: str = "无权限访问") -> None:
        super().__init__(message, code=403)


class ValidationError(AppBaseError):
    """业务校验失败。"""

    def __init__(self, message: str = "参数校验失败") -> None:
        super().__init__(message, code=422)
