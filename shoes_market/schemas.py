import uuid
from typing import Generic, TypeVar
from pydantic import BaseModel, Field


M = TypeVar('M')


class PaginatedResponse(BaseModel, Generic[M]):
    count: int
    pages: int
    results: list[M]


class JWT(BaseModel):
    access: str
    refresh: str


class Session(BaseModel):
    session_id: uuid.UUID


class CreateSession(Session):
    code: str = Field(min_length=6, max_length=6, example='444444')
