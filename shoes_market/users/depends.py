from pydantic import BaseModel


class FilterUser(BaseModel):
    nickname: str | None = None
