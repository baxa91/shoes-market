from enum import StrEnum, auto


USER_SESSION_KEY = 'users:session:{}'
USER_SESSION_KEY_TTL = 60 * 5
CHANGE_EMAIL_SESSION_KEY = "change-email:{}"
RESET_PASSWORD_KEY = "reset-password:{}"
RESET_PASSWORD_TTL = 60 * 15


class GenderType(StrEnum):
    MALE = auto()
    FEMALE = auto()
