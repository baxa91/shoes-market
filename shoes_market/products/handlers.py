import uuid
from typing import NamedTuple, Annotated

from fastapi import Request, Depends, Query

from shoes_market import schemas as core_schemas, constants as core_const

from . import models, services, schemas, depends, constants


class ProductHandler(NamedTuple):
    service: services.ProductServiceInterface

    async def create_tag(self, data: schemas.CreateTag) -> schemas.Tag:
        return await self.service.create_tag(data=data)

    async def get_tag(self, pk: uuid.UUID) -> schemas.Tag:
        return await self.service.get_tag(filters=(models.Tag.id == pk,))

    async def get_tags(self) -> list[schemas.Tag]:
        return await self.service.get_tags()

    async def update_tag(self, pk: uuid.UUID, data: schemas.CreateTag) -> schemas.Tag:
        return await self.service.update_tag(filters=(models.Tag.id == pk,), data=data)

    async def delete_tag(self, pk: uuid.UUID) -> dict:
        await self.service.delete_tag(filters=(models.Tag.id == pk,))
        return {'success': constants.DELETE_TAG}

    async def create_product(
            self, request: Request, data: schemas.CreateProduct) -> models.Product:
        core_const.REQUEST.update({
            'host': request.headers.get("host"),
            'scheme': request.url.scheme
        })
        return await self.service.create_product(data=data)

    async def get_products(
            self,
            request: Request,
            filters: Annotated[depends.FilterProduct, Depends()],
            tags: Annotated[list[str] | None, Query()] = None
    ) -> core_schemas.PaginatedResponse[schemas.Product]:
        core_const.REQUEST.update({
            'host': request.headers.get("host"),
            'scheme': request.url.scheme
        })
        return await self.service.get_products(filters, tags)

    async def get_product(self, request: Request, pk: uuid.UUID) -> schemas.Product:
        core_const.REQUEST.update({
            'host': request.headers.get("host"),
            'scheme': request.url.scheme
        })
        return await self.service.get_product(filters=(models.Product.id == pk,))

    async def delete_product(self, pk: uuid.UUID) -> dict:
        await self.service.delete_product(pk)
        return {'success': constants.DELETE_PRODUCT}

    async def update_product(
            self, request: Request, pk: uuid.UUID, data: schemas.UpdateProduct
    ) -> schemas.Product:
        core_const.REQUEST.update({
            'host': request.headers.get("host"),
            'scheme': request.url.scheme
        })
        return await self.service.update_product(pk, data)
