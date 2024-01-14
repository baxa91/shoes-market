from typing import Any

from fastapi import HTTPException, status


class Unauthorized(HTTPException):

    def __init__(
        self, status_code: int = status.HTTP_401_UNAUTHORIZED,
        detail: Any = 'Unauthorized',
        headers: dict | None = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class RedisUrlNotFound(HTTPException):

    def __init__(
        self, status_code: int = status.HTTP_404_NOT_FOUND,
        detail: Any = 'Redis url not found',
        headers: dict | None = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class NotFound(HTTPException):

    def __init__(
        self, status_code: int = status.HTTP_404_NOT_FOUND,
        detail: Any = 'Not found',
        headers: dict | None = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class PermissionDenied(HTTPException):

    def __init__(
        self, status_code: int = status.HTTP_403_FORBIDDEN,
        detail: Any = 'Permission denied',
        headers: dict | None = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)