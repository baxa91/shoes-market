from pydantic import BaseModel
from fastapi import Request
from shoes_market import exceptions


class FilterUser(BaseModel):
    nickname: str | None = None


async def is_authenticated(request: Request):
    if not request.state.is_authenticated:
        raise exceptions.Unauthorized
