import datetime as dt
import uuid

from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict

from sqlalchemy import exists

from shoes_market import constants, database

from . import exceptions, models


class ListUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nickname: str | None


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nickname: str | None
    phone_number: str = Field(json_schema_extra={
        'example': '+77777777777',
    })
    email: EmailStr
    first_name: str = Field(json_schema_extra={
        'example': 'John',
    })
    last_name: str = Field(json_schema_extra={
        'example': 'Doe',
    })
    birth_date: dt.date | None
    gender: constants.GenderType | None


class CreateUser(BaseModel):
    nickname: str | None
    phone_number: str = Field(json_schema_extra={
        'example': '+77777777777',
    })
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str = Field(json_schema_extra={
        'example': 'John',
    })
    last_name: str = Field({
        'example': 'Doe',
    })

    @field_validator('phone_number')
    def validate_phone_number(cls, phone_number: str):
        query = exists().where(models.User.phone_number == phone_number)

        with database.session() as session:
            if session.query(query).scalar():
                raise exceptions.PhoneNumberAlreadyExistException

        return phone_number


class UpdateUser(BaseModel):
    nickname: str | None = None
    first_name: str | None = Field({
        'example': 'John',
    })
    last_name: str | None = Field({
        'example': 'Doe',
    })
    phone_number: str = Field({
        'example': '+77777777777',
    })
    birth_date: dt.date | None = None
    gender: constants.GenderType | None = None


class CreateJWT(BaseModel):
    phone_number: str = Field(json_schema_extra={
        'example': '+77777777777',
    })
    password: str = Field(min_length=8, max_length=64)

    @field_validator('phone_number')
    def validate_phone_number(cls, phone_number: str):
        query = exists().where(models.User.phone_number == phone_number)

        with database.session() as session:
            if not session.query(query).scalar():
                raise exceptions.PhoneNumberNotFoundExistException

        return phone_number


class RefreshJWT(BaseModel):
    refresh: str
