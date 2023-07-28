from gettext import gettext as _


class PriceNegativeException(ValueError):

    def __init__(self, *args):
        super().__init__(_('Цена указано не правильно'), *args)


class ExistNameException(ValueError):

    def __init__(self, *args):
        super().__init__(_('Такой тэг уже существует'), *args)


class ImageCountException(ValueError):

    def __init__(self, *args):
        super().__init__(_('Количество фото превышает допустимого'), *args)


class ImageTypeException(ValueError):

    def __init__(self, *args):
        super().__init__(
            _('Недопустимый тип файла. Поддерживаются только форматы JPEG, PNG, GIF и WebP'),
            *args
        )


class ImageBaseException(ValueError):

    def __init__(self, *args):
        super().__init__(
            _('Главное фото, может быть только одна'), *args)


class DoesNotExistsException(ValueError):

    def __init__(self, *args):
        super().__init__(_('Объект не существует'), *args)
