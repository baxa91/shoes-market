from typing import NamedTuple, Protocol

from sqlalchemy import delete, insert, select, update
from shoes_market import pagination, schemas as core_schemas, database, utils

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
            filters = self._filters(**filter_kwargs)
            rows = await session.scalars(
                update(self.model).returning(self.model).where(*filters).values(**kwargs),
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
