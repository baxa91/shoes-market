import json
import uuid

from typing import NamedTuple, Protocol, NoReturn, Annotated

from redis import asyncio as aioredis
from fastapi import Depends, Query
from sqlalchemy import and_, or_

from . import models, repos, schemas, depends
from shoes_market import schemas as core_schemas


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

    async def get_products(
            self,
            filters: Annotated[depends.FilterProduct, Depends()],
            tags: Annotated[list[str] | None, Query()] = None
    ) -> core_schemas.PaginatedResponse[schemas.Product]:
        ...

    async def get_product(self, filters: tuple = ()) -> schemas.Product:
        ...

    async def delete_product(self, pk: uuid.UUID) -> NoReturn:
        ...

    async def update_product(self, pk: uuid.UUID, data: schemas.UpdateProduct) -> schemas.Product:
        ...

    async def create_product_image(self, data: schemas.CreateProductImage) -> schemas.ProductImage:
        ...

    async def update_product_image(
            self, pk: uuid.UUID, data: schemas.UpdateProductImage) -> NoReturn:
        ...

    async def delete_product_image(self, filters: tuple = ()) -> NoReturn:
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

    async def get_products(
            self,
            filters: Annotated[depends.FilterProduct, Depends()],
            tags: Annotated[list[str] | None, Query()] = None
    ) -> core_schemas.PaginatedResponse[schemas.Product]:
        key = f'{filters.model_dump()}{tags}'
        cache = await self.redis.get(key)
        if cache:
            return json.loads(cache)

        tag_list = [models.Product.tags.any(models.Tag.id == tag) for tag in tags] if tags else []

        prices = [
            models.Product.price >= filters.price_before if filters.price_before else None,
            models.Product.price <= filters.price_after if filters.price_after else None
        ]
        prices = [price for price in prices if price is not None]

        filters_orm = or_(*tag_list) if not prices else and_(or_(*tag_list), *prices)
        products = await self.repo.get_products(filters.page, filters.page_size, filters_orm)
        await self.redis.setex(key, 500, products.model_dump_json())
        return products

    async def get_product(self, filters: tuple = ()) -> schemas.Product:
        return await self.repo.get_product(filters)

    async def delete_product(self, pk: uuid.UUID) -> NoReturn:
        await self.repo.delete_product(pk)

    async def update_product(self, pk: uuid.UUID, data: schemas.UpdateProduct) -> schemas.Product:
        return await self.repo.update_product(pk, data)

    async def create_product_image(self, data: schemas.CreateProductImage) -> schemas.ProductImage:
        return await self.repo.create_product_image(data)

    async def update_product_image(
            self, pk: uuid.UUID, data: schemas.UpdateProductImage) -> NoReturn:
        await self.repo.update_product_image(pk, data)

    async def delete_product_image(self, filters: tuple = ()) -> NoReturn:
        await self.repo.delete_product_image(filters)
