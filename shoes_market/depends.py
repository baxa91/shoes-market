from pydantic import BaseModel

from fastapi import Query


class PaginatedParams(BaseModel):
    page: int = Query(1, ge=1)
    page_size: int = Query(8, gt=0)
