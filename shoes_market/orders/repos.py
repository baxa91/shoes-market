from typing import Protocol, NamedTuple

from sqlalchemy import select, asc
from sqlalchemy.orm import joinedload

from shoes_market import database, schemas as core_schemas, pagination
from shoes_market.orders import models, schemas


class OrderRepoInterface(Protocol):

    @staticmethod
    async def create_order(**kwargs) -> models.Order:
        ...

    @staticmethod
    async def get_orders(
            page: int, page_size: int, filters
    ) -> core_schemas.PaginatedResponse[schemas.ListOrder]:
        ...


class OrderRepoV1(NamedTuple):

    @staticmethod
    async def create_order(**kwargs) -> models.Order:
        return await models.Order.create(db_session=database.async_session(), data=kwargs)

    @staticmethod
    async def get_orders(
            page: int, page_size: int, filters
    ) -> core_schemas.PaginatedResponse[schemas.ListOrder]:
        query = select(models.Order).where(filters).order_by(
            asc(models.Order.created_at)
        ).options(joinedload(models.Order.client), joinedload(models.Order.product))
        return await pagination.paginate(
            database.async_session(), query,
            page, page_size, schemas.ListOrder
        )
