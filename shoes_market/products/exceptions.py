from gettext import gettext as _
from typing import Any

from fastapi import HTTPException, status


class PriceNegativeException(ValueError):

    def __init__(self, *args):
        super().__init__(_('Цена указано не правильно'), *args)


class ExistNameException(ValueError):

    def __init__(self, *args):
        super().__init__(_('Такой тэг уже существует'), *args)


class ImageCountException(ValueError):

    def __init__(self, *args):
        super().__init__(_('Количество фото превышает допустимого'), *args)


class ImageTypeException(HTTPException):

    def __init__(
        self, status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: Any = 'Недопустимый тип файла. Поддерживаются только форматы JPEG, PNG, GIF и WebP',
        headers: dict | None = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class ImageBaseException(ValueError):

    def __init__(self, *args):
        super().__init__(
            _('Главное фото, может быть только одна'), *args)
