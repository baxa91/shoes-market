from typing import NamedTuple, Protocol, NoReturn

from redis import asyncio as aioredis

from . import models, repos, schemas


class ProductServiceInterface(Protocol):

    async def create_tag(self, data: schemas.CreateTag) -> models.Tag:
        ...

    async def get_tag(self, filters: tuple = ()) -> models.Tag:
        ...

    async def get_tags(self) -> list[schemas.Tag]:
        ...

    async def update_tag(self, filters: tuple, data: schemas.CreateTag) -> schemas.Tag:
        ...

    async def delete_tag(self, filters: tuple = ()) -> NoReturn:
        ...

    async def create_product(self, data: schemas.CreateProduct) -> models.Product:
        ...


class ProductServiceV1(NamedTuple):
    repo: repos.ProductRepoInterface
    redis: aioredis.Redis

    async def create_tag(self, data: schemas.CreateTag) -> models.Tag:
        return await self.repo.create_tag(data)

    async def get_tag(self, filters: tuple = ()) -> models.Tag:
        return await self.repo.get_tag(filters)

    async def get_tags(self) -> list[schemas.Tag]:
        return await self.repo.get_tags()

    async def update_tag(self, filters: tuple, data: schemas.CreateTag) -> schemas.Tag:
        return await self.repo.update_tag(filters, data)

    async def delete_tag(self, filters: tuple = ()) -> NoReturn:
        await self.repo.delete_tag(filters)

    async def create_product(self, data: schemas.CreateProduct) -> models.Product:
        return await self.repo.create_product(data)
