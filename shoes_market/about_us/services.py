import uuid
from typing import NamedTuple, Protocol
from redis import asyncio as aioredis
from . import repos, schemas
from shoes_market import utils


class AboutUsServiceInterface(Protocol):

    async def create_about_us(self, data: dict) -> None:
        ...

    async def get_about_us(self) -> schemas.AboutUs:
        ...

    async def update_about_us(self, data: dict) -> None:
        ...

    async def create_about_image(self, data: dict) -> None:
        ...

    async def delete_about_image(self, pk: uuid.UUID) -> None:
        ...

    async def create_contact_page(self, data: dict) -> None:
        ...

    async def update_contact_page(self, data: dict) -> None:
        ...

    async def get_contact_page(self) -> schemas.ContactPage:
        ...


class AboutUsServiceV1(NamedTuple):
    repo: repos.AboutUsRepoInterface
    redis: aioredis.Redis

    async def create_about_us(self, data: dict) -> None:
        await self.repo.create_about_us(data=data)

    async def get_about_us(self) -> schemas.AboutUs:
        return await self.repo.get_about_us()

    async def update_about_us(self, data: dict) -> None:
        await self.repo.update_about_us(data=data)

    async def create_about_image(self, data: dict) -> None:
        image_url = await utils.storage.upload_base64_image(
            base64_image=data.pop("image"),
            folder="about_us",
        )
        data['image'] = image_url
        await self.repo.create_about_image(data=data)

    async def delete_about_image(self, pk: uuid.UUID) -> None:
        await self.repo.delete_about_image(pk=pk)

    async def create_contact_page(self, data: dict) -> None:
        await self.repo.create_contact_page(data=data)

    async def update_contact_page(self, data: dict) -> None:
        await self.repo.update_contact_page(data=data)

    async def get_contact_page(self) -> schemas.ContactPage:
        return await self.repo.get_contact_page()
