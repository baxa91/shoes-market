import datetime as dt

from sqlalchemy import ARRAY, DateTime, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from shoes_market import constants
from shoes_market.models import BaseModel


class User(BaseModel):
    __tablename__ = 'users_user'

    nickname: Mapped[str] = mapped_column(String(200), nullable=True, index=True)
    phone_number: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password: Mapped[str] = mapped_column(Text())
    image: Mapped[str] = mapped_column(String(500), nullable=True)
    first_name: Mapped[str] = mapped_column(String(255))
    last_name: Mapped[str] = mapped_column(String(255))
    gender: Mapped[constants.GenderType] = mapped_column(Enum(constants.GenderType), nullable=True)
    birth_date: Mapped[dt.date] = mapped_column(nullable=True)
    telegram_id: Mapped[str] = mapped_column(String(255), nullable=True)
    is_staff: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=False)
    last_login: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=True)
