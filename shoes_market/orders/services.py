import uuid
from typing import Protocol, NamedTuple, Annotated

from fastapi import Depends

from shoes_market.orders import schemas, models, repos, depends
from shoes_market import schemas as core_schemas


class OrderServiceInterface(Protocol):

    async def create_order(self, client_id: uuid.UUID, data: schemas.CreateOrder) -> models.Order:
        ...

    async def get_orders(
            self, filters: Annotated[depends.FilterOrder, Depends()]
    ) -> core_schemas.PaginatedResponse[schemas.ListOrder]:
        ...


class OrderServiceV1(NamedTuple):
    repo: repos.OrderRepoInterface

    async def create_order(self, client_id: uuid.UUID, data: schemas.CreateOrder) -> models.Order:
        data_dict = data.model_dump(exclude_unset=True)
        data_dict['client_id'] = client_id
        return await self.repo.create_order(**data_dict)

    async def get_orders(
            self, filters: Annotated[depends.FilterOrder, Depends()]
    ) -> core_schemas.PaginatedResponse[schemas.ListOrder]:
        filters_tuple = (models.Order.status == models.OrderStatus.PROCESSING)
        if filters.status:
            filters_tuple = (models.Order.status == filters.status)

        return await self.repo.get_orders(
            filters.page, filters.page_size, filters_tuple
        )
