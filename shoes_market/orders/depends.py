from shoes_market import depends
from shoes_market.orders.models import OrderStatus
from fastapi import Query


class FilterOrder(depends.PaginatedParams):
    status: OrderStatus | None = Query(default=None)
