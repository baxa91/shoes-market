import datetime as dt
import uuid
from typing import Self, NoReturn

from sqlalchemy import DateTime, insert, select, update, delete
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, selectinload

from shoes_market import exceptions


class Base(AsyncAttrs, DeclarativeBase):
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, index=True, default=uuid.uuid4)

    @classmethod
    async def create(cls, db_session: AsyncSession, data: dict) -> Self:
        async with db_session as session, session.begin():
            rows = await session.scalars(insert(cls).returning(cls).values(**data))
            row = rows.one()
            session.expunge_all()
            await session.commit()

            return row

    @classmethod
    async def get(cls, db_session: AsyncSession, filters: tuple = (), *args) -> Self:
        async with db_session as session:
            if args:
                rows = await session.scalars(select(cls).options(
                    *[selectinload(getattr(cls, join)) for join in args]
                ).filter(*filters))
            else:
                rows = await session.scalars(select(cls).filter(*filters))

            row = rows.one_or_none()

        if not row:
            raise exceptions.NotFound

        return row

    @classmethod
    async def update(
            cls, db_session: AsyncSession, filters: tuple = (), data: dict = None) -> NoReturn:
        async with db_session as session, session.begin():
            query = update(cls).where(*filters).values(**data)
            await session.execute(query)
            await session.commit()

    @classmethod
    async def delete(cls, db_session: AsyncSession, filters: tuple = ()) -> NoReturn:
        async with db_session as session, session.begin():
            query = delete(cls).where(*filters)
            await session.execute(query)
            await session.commit()


class BaseModel(Base):
    __abstract__ = True

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=dt.datetime.now,
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=dt.datetime.now,
    )
