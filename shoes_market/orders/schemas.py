import uuid
import datetime as dt
from pydantic import BaseModel, ConfigDict, field_validator
from sqlalchemy import exists

from shoes_market import database, exceptions
from shoes_market.orders.models import OrderStatus
from shoes_market.products import models as product_models


class Client(BaseModel):
    id: uuid.UUID
    phone_number: str


class Product(BaseModel):
    id: uuid.UUID
    title: str
    price: int
    currency: str
    description: str


class Order(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    description: str
    ankle: float | None
    foot_length: float
    status: OrderStatus
    foot_width: float | None
    client_id: uuid.UUID
    product_id: uuid.UUID
    created_at: dt.datetime


class CreateOrder(BaseModel):
    description: str | None
    ankle: float | None = None
    foot_length: float
    foot_width: float | None = None
    product_id: uuid.UUID

    @field_validator('product_id')
    def validate_product(cls, product_id: uuid.UUID):
        query = exists().where(product_models.Product.id == product_id)

        with database.session() as session:
            if not session.query(query).scalar():
                raise exceptions.DoesNotExistsException

        return product_id


class ListOrder(BaseModel):
    id: uuid.UUID
    description: str
    ankle: float | None
    foot_length: float
    status: OrderStatus
    foot_width: float | None
    client: Client
    product: Product
