from typing import NamedTuple, Annotated
from fastapi import Request, Depends
from shoes_market.orders import services, schemas, models, depends
from shoes_market import schemas as core_schemas


class OrderHandler(NamedTuple):
    service: services.OrderServiceInterface

    async def create_order(self, request: Request, data: schemas.CreateOrder) -> models.Order:
        return await self.service.create_order(client_id=request.state.user.get('id'), data=data)

    async def get_orders(
            self, filters: Annotated[depends.FilterOrder, Depends()]
            ) -> core_schemas.PaginatedResponse[schemas.ListOrder]:
        return await self.service.get_orders(filters)
