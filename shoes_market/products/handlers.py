import uuid
from typing import NamedTuple, Annotated

from fastapi import Request, Depends, Query

from shoes_market import schemas as core_schemas

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
            self, data: schemas.CreateProduct) -> models.Product:
        return await self.service.create_product(data=data)

    async def get_products(
            self, request: Request,
            filters: Annotated[depends.FilterProduct, Depends()],
            tags: Annotated[list[str] | None, Query()] = None
    ) -> core_schemas.PaginatedResponse[schemas.Product]:
        if request.state.is_authenticated:
            return await self.service.get_products(filters, tags, request.state.user.get('id'))

        return await self.service.get_products(filters, tags)

    async def get_product(self, pk: uuid.UUID) -> schemas.DetailProduct:
        return await self.service.get_product(filters=(models.Product.id == pk,))

    async def delete_product(self, pk: uuid.UUID) -> dict:
        await self.service.delete_product(pk)
        return {'success': constants.DELETE_PRODUCT}

    async def update_product(
            self, pk: uuid.UUID, data: schemas.UpdateProduct
    ) -> schemas.Product:
        return await self.service.update_product(pk, data)

    async def create_product_image(
            self, data: schemas.CreateProductImageDetail
    ) -> schemas.ProductImage:
        return await self.service.create_product_image(data)

    async def update_product_image(self, pk: uuid.UUID, data: schemas.UpdateProductImage) -> dict:
        await self.service.update_product_image(pk, data)
        return {'success': constants.UPDATE_PRODUCT_IMAGE}

    async def delete_product_image(self, pk: uuid.UUID) -> dict:
        await self.service.delete_product_image(filters=(models.ProductImage.id == pk,))
        return {'success': constants.DELETE_PRODUCT_IMAGE}
