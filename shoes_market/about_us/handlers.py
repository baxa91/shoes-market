import uuid
from typing import NamedTuple, Annotated

from fastapi import Request, Depends, Query

from shoes_market import schemas as core_schemas

from . import models, services, schemas


class AboutUsHandler(NamedTuple):
    service: services.AboutUsServiceInterface

    async def create_about_us(self, data: schemas.CreateAboutUs) -> None:
        await self.service.create_about_us(data=data.model_dump(exclude_none=True))

    async def get_about_us(self) -> schemas.AboutUs:
        return await self.service.get_about_us()

    async def update_about_us(self, data: schemas.UpdateAboutUs) -> None:
        await self.service.update_about_us(data=data.model_dump(exclude_none=True))

    async def create_about_image(self, data: schemas.CreateAboutImage) -> None:
        await self.service.create_about_image(data=data.model_dump(exclude_none=True))

    async def delete_about_image(self, pk: uuid.UUID) -> None:
        await self.service.delete_about_image(pk)

    async def create_contact_page(self, data: schemas.CreateContactPage) -> None:
        await self.service.create_contact_page(data=data.model_dump(exclude_none=True))

    async def update_contact_page(self, data: schemas.CreateContactPage) -> None:
        await self.service.update_contact_page(data=data.model_dump(exclude_none=True))

    async def get_contact_page(self) -> schemas.ContactPage:
        return await self.service.get_contact_page()

