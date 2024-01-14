import uuid
import datetime as dt
from urllib.parse import urljoin

from pydantic import (
    BaseModel, Field, field_validator,
    ConfigDict, field_serializer, model_validator, Extra
)

from sqlalchemy import exists, select, func

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
    product_id: uuid.UUID
    image: str

    @field_serializer('image')
    def serialize_image(self, image: str):
        if not image:
            return None

        return urljoin(settings.MEDIA_URL, image)


class MiniProductImage(BaseModel):
    id: uuid.UUID
    image: str

    @field_serializer('image')
    def serialize_image(self, image: str):
        if not image:
            return None

        return urljoin(settings.MEDIA_URL, image)


class CreateProductImage(BaseModel):
    image: bytes


class Product(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    tags: list[Tag] = []
    price: int
    currency: str = Field(json_schema_extra={'example': 'KZT'})
    description: str
    main_image: str
    created_at: dt.datetime
    is_favorite: bool = False

    @field_serializer('main_image')
    def serialize_image(self, main_image: str):
        if not main_image:
            return None

        return urljoin(settings.MEDIA_URL, main_image)


class DetailProduct(BaseModel):
    id: uuid.UUID
    title: str
    tags: list[Tag] = []
    price: int
    currency: str = Field(json_schema_extra={'example': 'KZT'})
    description: str
    main_image: str
    images: list[MiniProductImage]
    created_at: dt.datetime

    @field_serializer('main_image')
    def serialize_image(self, main_image: str):
        if not main_image:
            return None

        return urljoin(settings.MEDIA_URL, main_image)


class CreateProduct(BaseModel):
    title: str
    price: int
    tags: list[uuid.UUID]
    currency: str = Field(json_schema_extra={'example': 'KZT'})
    description: str
    main_image: bytes

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


class UpdateProduct(BaseModel):
    title: str | None = None
    price: int | None = None
    tags: list[uuid.UUID] | None = None
    currency: str | None = Field(json_schema_extra={'example': 'KZT'}, default=None)
    description: str | None = None
    is_active: bool | None = None

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


class CreateProductImageDetail(CreateProductImage):
    product_id: uuid.UUID

    @field_validator('product_id')
    def validate_product_id(cls, product_id: uuid.UUID):
        query = exists().where(models.Product.id == product_id)
        with database.session() as session:
            if not session.query(query).scalar():
                raise exceptions.DoesNotExistsException

            rows = select(models.ProductImage).where(models.ProductImage.product_id == product_id)
            count = session.scalar(select(func.count()).select_from(rows))
            if count > 7:
                raise exceptions.ImageCountException

        return product_id

    @model_validator(mode='after')
    def validate_is_base(self):
        if self.is_base:
            query = exists().where(
                models.ProductImage.product_id == self.product_id
            )
            with database.session() as session:
                if session.query(query).scalar():
                    raise exceptions.ImageBaseException

        return self


class UpdateProductImage(BaseModel):
    product_id: uuid.UUID

    @field_validator('product_id')
    def validate_product_id(cls, product_id: uuid.UUID):
        query = exists().where(models.Product.id == product_id)
        with database.session() as session:
            if not session.query(query).scalar():
                raise exceptions.DoesNotExistsException

        return product_id

    @model_validator(mode='after')
    def validate_is_base(self):
        if self.is_base:
            query = exists().where(
                models.ProductImage.product_id == self.product_id
            )
            with database.session() as session:
                if session.query(query).scalar():
                    raise exceptions.ImageBaseException

        return self
