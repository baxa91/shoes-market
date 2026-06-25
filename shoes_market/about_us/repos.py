import uuid
from typing import NamedTuple, Protocol

from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from shoes_market import database, utils

from . import models, schemas


class AboutUsRepoInterface(Protocol):

    @staticmethod
    async def create_about_us(data: dict) -> None:
        ...

    @staticmethod
    async def get_about_us() -> schemas.AboutUs:
        ...

    @staticmethod
    async def update_about_us(data: dict) -> None:
        ...

    @staticmethod
    async def create_about_image(data: dict) -> None:
        ...

    @staticmethod
    async def delete_about_image(pk: uuid.UUID) -> None:
        ...

    @staticmethod
    async def create_contact_page(data: dict) -> None:
        ...

    @staticmethod
    async def update_contact_page(data: dict) -> None:
        ...

    @staticmethod
    async def get_contact_page() -> schemas.ContactPage:
        ...


class AboutUsRepoV1(NamedTuple):

    @staticmethod
    async def create_about_us(data: dict) -> None:
        async with database.async_session() as session:
            about = await session.scalar(
                select(models.AboutUs)
            )

            if about:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Страница 'О нас' уже существует"
                )

            about = models.AboutUs(
                title=data["title"],
                subtitle=data.get("subtitle"),
                content=data["content"],
            )

            session.add(about)
            await session.commit()

    @staticmethod
    async def get_about_us() -> schemas.AboutUs | None:
        async with database.async_session() as session:
            about = await session.scalar(
                select(models.AboutUs)
                .options(selectinload(models.AboutUs.images))
            )

            return about

    @staticmethod
    async def update_about_us(data: dict) -> None:
        async with database.async_session() as session:
            about = await session.scalar(select(models.AboutUs))

            if not about:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Страница 'О нас' не найдена"
                )

            for key, value in data.items():
                if value is not None:
                    setattr(about, key, value)

            await session.commit()

    @staticmethod
    async def create_about_image(data: dict) -> None:
        async with database.async_session() as session:
            about = await session.scalar(select(models.AboutUs))

            if not about:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Сначала создайте страницу 'О нас'"
                )

            image = models.AboutImage(
                about_id=about.id,
                image=data["image"],
                sort_order=data.get("sort_order", 0),
            )

            session.add(image)
            await session.commit()

    @staticmethod
    async def delete_about_image(pk: uuid.UUID) -> None:
        async with database.async_session() as session:
            image = await session.get(models.AboutImage, pk)

            if not image:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Фото не найдено"
                )

            if image.image:
                utils.storage.delete_file_by_url(image.image)

            await session.delete(image)
            await session.commit()

    @staticmethod
    async def create_contact_page(data: dict) -> None:
        async with database.async_session() as session:
            contact = await session.scalar(select(models.ContactPage))

            if contact:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Страница контактов уже существует"
                )

            phones_data = data.pop("phones", [])

            contact = models.ContactPage(
                instagram=data.get("instagram"),
                address=data.get("address"),
                map_url=data.get("map_url"),
                work_hours=data.get("work_hours"),
            )

            session.add(contact)
            await session.flush()

            for phone_data in phones_data:
                phone = models.ContactPhone(
                    contact_page_id=contact.id,
                    phone=phone_data["phone"],
                    title=phone_data.get("title"),
                    is_whatsapp=phone_data.get("is_whatsapp", False),
                    sort_order=phone_data.get("sort_order", 0),
                )
                session.add(phone)

            await session.commit()

    @staticmethod
    async def update_contact_page(data: dict) -> None:
        async with database.async_session() as session:
            contact = await session.scalar(
                select(models.ContactPage)
                .options(selectinload(models.ContactPage.phones))
            )

            if not contact:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Страница контактов не найдена"
                )

            phones_data = data.pop("phones", None)

            for key, value in data.items():
                if value is not None:
                    setattr(contact, key, value)

            if phones_data is not None:
                await session.execute(
                    delete(models.ContactPhone)
                    .where(models.ContactPhone.contact_page_id == contact.id)
                )

                for phone_data in phones_data:
                    phone = models.ContactPhone(
                        contact_page_id=contact.id,
                        phone=phone_data["phone"],
                        title=phone_data.get("title"),
                        is_whatsapp=phone_data.get("is_whatsapp", False),
                        sort_order=phone_data.get("sort_order", 0),
                    )
                    session.add(phone)

            await session.commit()

    @staticmethod
    async def get_contact_page() -> schemas.ContactPage | None:
        async with database.async_session() as session:
            contact = await session.scalar(
                select(models.ContactPage)
                .options(selectinload(models.ContactPage.phones))
            )

            return contact