import uuid
from typing import NamedTuple
from urllib.parse import urljoin

from fastapi import Request

from shoes_market import settings

from . import models, services, schemas


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
        return {'success': 'delete tag'}

    async def create_product(
            self, request: Request, data: schemas.CreateProduct) -> models.Product:
        product = await self.service.create_product(data=data)
        host = request.headers.get("host")
        scheme = request.url.scheme
        for image in product.images:
            image.image = urljoin(f"{scheme}://{host}/{settings.MEDIA_PATH}", image.image)

        return product
