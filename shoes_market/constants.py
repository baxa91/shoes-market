from enum import StrEnum, auto


USER_SESSION_KEY = 'users:session:{}'
USER_SESSION_KEY_TTL = 60 * 5


class GenderType(StrEnum):
    MALE = auto()
    FEMALE = auto()
