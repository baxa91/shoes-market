from typing import Any

from fastapi import HTTPException, status


class CommonException(HTTPException):

    def __init__(
            self, status_code: int = status.HTTP_400_BAD_REQUEST,
            detail: Any = 'Пароль меньше 8 символов',
            headers: dict | None = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)
