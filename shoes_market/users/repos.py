import uuid
from typing import NamedTuple, Protocol
from sqlalchemy import delete, insert, select, update
from shoes_market import pagination, schemas as core_schemas, database, utils
from fastapi import HTTPException, status

from . import exceptions, models, schemas


class UserRepoInterface(Protocol):

    async def create_user(self, data: schemas.CreateUser) -> models.User:
        ...

    async def get_user(self, **kwargs) -> models.User:
        ...

    @staticmethod
    async def get_users(
            page: int, page_size: int, filters: tuple = ()
    ) -> core_schemas.PaginatedResponse[schemas.ListUser]:
        ...

    async def update_user(self, filter_kwargs: dict | None = None, **kwargs) -> models.User:
        ...

    @staticmethod
    async def get_user_by_email(email: str) -> None:
        ...

    @staticmethod
    async def update_user_password(user_id: str, password: str) -> None:
        ...

    @staticmethod
    async def change_password(
            user_id: uuid.UUID,
            old_password: str,
            new_password: str,
    ) -> None:
        ...


class UserRepoV1(NamedTuple):
    model = models.User

    async def create_user(self, data: schemas.CreateUser) -> models.User:
        async with database.async_session() as session, session.begin():
            rows = await session.scalars(
                insert(self.model).returning(self.model).values(**data.model_dump()),
            )
            user = rows.one()
            session.expunge_all()

            return user

    async def get_user(self, verify_password: bool = False, **kwargs) -> models.User:
        password = kwargs.pop('password', '')
        filters = [getattr(self.model, k) == v for k, v in kwargs.items()]

        if not filters and not password:
            raise exceptions.UserNotFoundException

        async with database.async_session() as session:
            rows = await session.scalars(select(self.model).where(*filters))

            user = rows.one_or_none()

            if not user:
                raise exceptions.UserNotFoundException

            if not verify_password:
                return user

            if utils.verify_password(password, user.password):
                return user

            raise exceptions.UserNotFoundException

    @staticmethod
    async def get_users(
            page: int, page_size: int, filters: tuple = ()
    ) -> core_schemas.PaginatedResponse[schemas.ListUser]:
        return await pagination.paginate(
            database.async_session(), select(models.User).where(*filters), page, page_size,
        )

    async def update_user(self, filter_kwargs: dict | None = None, **kwargs) -> models.User:

        async with database.async_session() as session:

            if "phone_number" in kwargs:
                filters = self._filters(**filter_kwargs)

                current_user = await session.scalar(
                    select(self.model).where(*filters)
                )

                exists = await session.scalar(
                    select(self.model).where(
                        self.model.phone_number == kwargs["phone_number"],
                        self.model.id != current_user.id
                    )
                )

                if exists:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Пользователь с таким номером уже существует"
                    )

            filters = self._filters(**filter_kwargs)

            rows = await session.scalars(
                update(self.model)
                .returning(self.model)
                .where(*filters)
                .values(**kwargs),
            )

            try:
                user = rows.one()
            except Exception:
                raise exceptions.UserNotFoundException

            session.expunge_all()
            await session.commit()

            return user

    async def delete_user(self, **kwargs):

        async with database.async_session() as session:
            filters = self._filters(**kwargs)
            await session.execute(delete(self.model).where(*filters))
            await session.commit()

    def _filters(self, **kwargs):
        if not kwargs:
            kwargs = {}

        return [getattr(self.model, k) == v for k, v in kwargs.items()]


    @staticmethod
    async def get_user_by_email(email: str) -> None:
        async with database.async_session() as session:
            return await session.scalar(
                select(models.User).where(
                    models.User.email == email
                )
            )

    @staticmethod
    async def update_user_password(user_id: str, password: str) -> None:
        async with database.async_session() as session:
            user = await session.get(models.User, user_id)

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Пользователь не найден"
                )

            user.password = password

            await session.commit()

    @staticmethod
    async def change_password(
            user_id: uuid.UUID,
            old_password: str,
            new_password: str,
    ) -> None:
        async with database.async_session() as session:
            user = await session.get(models.User, user_id)

            if not user:
                raise exceptions.UserNotFoundException

            if not utils.verify_password(old_password, user.password):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Неверный текущий пароль",
                )

            user.password = utils.hash_password(new_password)

            await session.commit()
