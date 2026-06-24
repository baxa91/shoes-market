from typing import NamedTuple, Annotated

from fastapi import Depends, Request

from shoes_market import schemas as core_schemas, depends as core_depends
from sqlalchemy.sql.functions import user

from . import depends, schemas, services, models


class UserHandler(NamedTuple):
    service: services.UserServiceInterface

    async def create_user_session(self, data: schemas.CreateUser) -> core_schemas.Session:
        return await self.service.create_user_session(data=data)

    async def create_user(self, data: core_schemas.CreateSession) -> schemas.User:
        return await self.service.create_user(data=data)

    async def create_jwt(self, data: schemas.CreateJWT) -> core_schemas.JWT:
        return await self.service.create_jwt(data=data)

    async def update_user(self, request: Request, data: schemas.UpdateUser) -> schemas.User:
        return await self.service.update_user(user_id=request.state.user.get('id'), data=data)

    async def get_user(self, request: Request) -> schemas.User:
        return await self.service.get_user(user_id=request.state.user.get('id'))

    async def get_users(
        self,
        pagination: Annotated[core_depends.PaginatedParams, Depends()],
        filters: Annotated[depends.FilterUser, Depends()],
    ) -> core_schemas.PaginatedResponse[schemas.ListUser]:
        filters = filters.model_dump(exclude_unset=True)
        nickname = filters.pop('nickname', None)
        if nickname:
            filters = (
                models.User.nickname.icontains(nickname),
                models.User.is_active.is_(True),
            )
        else:
            filters = (
                models.User.is_active.is_(True),
            )

        return await self.service.get_users(pagination.page, pagination.page_size, filters)

    async def refresh_jwt(self, data: schemas.RefreshJWT) -> core_schemas.JWT:
        return await self.service.refresh_jwt(data=data)

    async def forgot_password(self, data: schemas.ForgotPassword) -> None:
        await self.service.forgot_password(data=data.model_dump())

    async def reset_password(self, data: schemas.ResetPassword) -> None:
        await self.service.reset_password(data=data.model_dump())

    async def change_password(self, request: Request, data: schemas.ChangePassword) -> None:
        await self.service.change_password(user_id=request.state.user.get('id'), data=data.model_dump())

    async def change_email_session(self, request: Request, data: schemas.ForgotPassword) -> core_schemas.Session:
        return await self.service.change_email_session(request.state.user, data=data.model_dump())

    async def change_email(self, data: core_schemas.CreateSession) -> None:
        await self.service.change_email(data=data.model_dump())

