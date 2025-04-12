from pydantic import BaseModel

from fastapi import Query, Request

from shoes_market import exceptions


class PaginatedParams(BaseModel):
    page: int = Query(1, ge=1)
    page_size: int = Query(8, gt=0)


async def is_authenticated(request: Request):
    if not request.state.is_authenticated:
        raise exceptions.Unauthorized


async def is_admin(request: Request):
    if not request.state.user['is_staff']:
        raise exceptions.PermissionDenied
