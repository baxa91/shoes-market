from shoes_market import depends
from fastapi import Query


class FilterProduct(depends.PaginatedParams):
    price_after: int | None = Query(default=None)
    price_before: int | None = Query(default=None)
    creasing: bool | None = Query(default=None)
    favorites: bool | None = Query(default=None)
