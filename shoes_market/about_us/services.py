import uuid
import base64
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
        file = base64.b64decode(data.pop('image'))
        file_path = await utils.create_mediafile('about_us/', file)
        data['image'] = file_path
        await self.repo.create_about_image(data=data)

    async def delete_about_image(self, pk: uuid.UUID) -> None:
        await self.repo.delete_about_image(pk=pk)

    async def create_contact_page(self, data: dict) -> None:
        await self.repo.create_contact_page(data=data)

    async def update_contact_page(self, data: dict) -> None:
        await self.repo.update_contact_page(data=data)

    async def get_contact_page(self) -> schemas.ContactPage:
        return await self.repo.get_contact_page()
