from typing import Any

from fastapi import HTTPException, status


class UserNotFoundException(HTTPException):

    def __init__(
        self, status_code: int = status.HTTP_404_NOT_FOUND,
        detail: Any = 'User not found',
        headers: dict | None = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class PhoneNumberNotFoundExistException(ValueError):

    def __init__(self, *args):
        super().__init__('Phone number not found', *args)


class PhoneNumberAlreadyExistException(HTTPException):

    def __init__(
            self, status_code: int = status.HTTP_400_BAD_REQUEST,
            detail: Any = 'Такой номер телефона уже существует',
            headers: dict | None = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class EmailAlreadyExistException(ValueError):

    def __init__(self, *args):
        super().__init__('Email already exist', *args)
