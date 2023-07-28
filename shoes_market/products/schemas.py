import uuid
import datetime as dt
from urllib.parse import urljoin

from pydantic import BaseModel, Field, field_validator, ConfigDict, field_serializer

from sqlalchemy import exists

from shoes_market import database, settings, constants
from . import exceptions, models


class Tag(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str


class CreateTag(BaseModel):
    name: str

    @field_validator('name')
    def validate_name(cls, name: str):
        query = exists().where(models.Tag.name == name)

        with database.session() as session:
            if session.query(query).scalar():
                raise exceptions.ExistNameException

        return name


class ProductImage(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_base: bool = False
    image: str

    @field_serializer('image')
    def serialize_image(self, image: str):
        return urljoin(
            f"{constants.REQUEST.get('scheme')}://"
            f"{constants.REQUEST.get('host')}/{settings.MEDIA_PATH}", image
        )


class CreateProductImage(BaseModel):

    is_base: bool = False
    filename: str
    filetype: str
    image: bytes

    @field_validator('filetype')
    def validate_filetype(cls, filetype: str):
        allowed_filetypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if filetype not in allowed_filetypes:
            raise exceptions.ImageTypeException

        return filetype


class Product(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    tags: list[Tag] = []
    price: int
    currency: str = Field(json_schema_extra={'example': 'KZT'})
    description: str
    images: list[ProductImage] = []
    created_at: dt.datetime


class CreateProduct(BaseModel):
    title: str
    price: int
    tags: list[uuid.UUID]
    currency: str = Field(json_schema_extra={'example': 'KZT'})
    description: str
    images: list[CreateProductImage]

    @field_validator('price')
    def validate_price(cls, price: int):
        if price <= 0:
            raise exceptions.PriceNegativeException

        return price

    @field_validator('tags')
    def validate_tags(cls, tags: list):
        for tag in tags:
            query = exists().where(models.Tag.id == tag)

            with database.session() as session:
                if not session.query(query).scalar():
                    raise exceptions.DoesNotExistsException

        return tags

    @field_validator('images')
    def validate_images(cls, images: list):
        if len(images) > 7:
            raise exceptions.ImageCountException

        count = []
        for image in images:
            image = image.model_dump()
            if image['is_base']:
                count.append(image)

        if len(count) > 1:
            raise exceptions.ImageBaseException

        return images


class UpdateProduct(BaseModel):
    title: str | None = None
    price: int | None = None
    tags: list[uuid.UUID] | None = None
    currency: str | None = Field(json_schema_extra={'example': 'KZT'}, default=None)
    description: str | None = None

    @field_validator('price')
    def validate_price(cls, price: int):
        if price <= 0:
            raise exceptions.PriceNegativeException

        return price

    @field_validator('tags')
    def validate_tags(cls, tags: list):
        for tag in tags:
            query = exists().where(models.Tag.id == tag)

            with database.session() as session:
                if not session.query(query).scalar():
                    raise exceptions.DoesNotExistsException

        return tags
