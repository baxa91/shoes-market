class PriceNegativeException(ValueError):

    def __init__(self, *args):
        super().__init__('Цена указано не правильно', *args)


class ExistNameException(ValueError):

    def __init__(self, *args):
        super().__init__('Такое тэг уже существует', *args)


class ImageCountException(ValueError):

    def __init__(self, *args):
        super().__init__('Количество фото превышает допустимого', *args)


class ImageTypeException(ValueError):

    def __init__(self, *args):
        super().__init__(
            'Недопустимый тип файла. Поддерживаются только форматы JPEG, PNG, GIF и WebP', *args)


class ImageBaseException(ValueError):

    def __init__(self, *args):
        super().__init__(
            'Главное фото, может быть только одна', *args)


class DoesNotExistsException(ValueError):

    def __init__(self, *args):
        super().__init__('Объект не существует', *args)
