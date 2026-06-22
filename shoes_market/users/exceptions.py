from typing import Any

from fastapi import HTTPException, status


class UserNotFoundException(HTTPException):

    def __init__(
        self, status_code: int = status.HTTP_404_NOT_FOUND,
        detail: Any = 'User not found',
        headers: dict | None = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class EmailNotFoundExistException(ValueError):

    def __init__(self, *args):
        super().__init__('Email not found', *args)


class EmailAlreadyExistException(HTTPException):

    def __init__(
            self, status_code: int = status.HTTP_400_BAD_REQUEST,
            detail: Any = 'Такая почта уже существует',
            headers: dict | None = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)

class PhoneNumberAlreadyExistException(HTTPException):

    def __init__(
            self, status_code: int = status.HTTP_400_BAD_REQUEST,
            detail: Any = 'Такой номер уже существует',
            headers: dict | None = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)

class PasswordException(HTTPException):

    def __init__(
            self, status_code: int = status.HTTP_400_BAD_REQUEST,
            detail: Any = 'Пароль меньше 8 символов',
            headers: dict | None = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)