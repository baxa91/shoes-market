import uuid

from typing import NamedTuple, Protocol, NoReturn, Annotated

from redis import asyncio as aioredis
from fastapi import Depends, Query
from sqlalchemy import and_, or_, and_

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
            tags: Annotated[list[str] | None, Query()] = None, user_id: uuid.UUID = None
    ) -> core_schemas.PaginatedResponse[schemas.ListProduct]:
        ...

    async def get_product(self, filters: tuple = ()) -> schemas.DetailProduct:
        ...

    async def delete_product(self, pk: uuid.UUID) -> NoReturn:
        ...

    async def update_product(self, pk: uuid.UUID, data: schemas.UpdateProduct) -> schemas.Product:
        ...

    async def create_product_image(self, data: schemas.CreateProductImage) -> schemas.ProductImage:
        ...

    async def delete_product_image(self, filters: tuple = ()) -> NoReturn:
        ...

    async def like_dislike_product(self, **kwargs) -> None:
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
            tags: Annotated[list[str] | None, Query()] = None, user_id: uuid.UUID = None
    ) -> core_schemas.PaginatedResponse[schemas.ListProduct]:
        filters_list = [models.Product.is_active == True]
        if tags:
            filters_list.extend(models.Product.tags.any(models.Tag.id == tag) for tag in tags)
        if filters.price_before:
            filters_list.append(models.Product.price >= filters.price_before)
        if filters.price_after:
            filters_list.append(models.Product.price <= filters.price_after)

        order_by = filters.creasing if filters.creasing is not None else None
        like = filters.favorites is True and user_id is not None

        return await self.repo.get_products(
            filters.page, filters.page_size, and_(*filters_list), order_by, user_id, like=like
        )

    async def get_product(self, filters: tuple = ()) -> schemas.DetailProduct:
        return await self.repo.get_product(filters)

    async def delete_product(self, pk: uuid.UUID) -> NoReturn:
        await self.repo.delete_product(pk)

    async def update_product(self, pk: uuid.UUID, data: schemas.UpdateProduct) -> schemas.Product:
        return await self.repo.update_product(pk, data)

    async def create_product_image(self, data: schemas.CreateProductImage) -> schemas.ProductImage:
        return await self.repo.create_product_image(data)

    async def delete_product_image(self, filters: tuple = ()) -> NoReturn:
        await self.repo.delete_product_image(filters)

    async def like_dislike_product(self, **kwargs) -> None:
        await self.repo.like_dislike_product(**kwargs)
