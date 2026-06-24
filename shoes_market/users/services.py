import json
import uuid
import jwt
from typing import NamedTuple, Protocol

from fastapi.responses import JSONResponse
from fastapi import HTTPException, status
from redis import asyncio as aioredis

from shoes_market import constants, schemas as core_schemas, utils, settings
from shoes_market.mail import email_service
from sqlalchemy.sql.functions import current_user

from . import models, repos, schemas


class UserServiceInterface(Protocol):  # pragma: no cover

    async def create_user_session(self, data: schemas.CreateUser) -> core_schemas.Session:
        ...

    async def create_user(self, data: core_schemas.CreateSession) -> models.User:
        ...

    async def update_user(self, user_id: uuid.UUID, data: schemas.UpdateUser) -> models.User:
        ...

    async def get_user(self, user_id: uuid.UUID) -> models.User:
        ...

    async def get_users(
            self, page: int, page_size: int, filters: tuple = ()
    ) -> core_schemas.PaginatedResponse[schemas.ListUser]:
        ...

    async def create_jwt(self, data: schemas.CreateJWT) -> core_schemas.JWT:
        ...

    async def refresh_jwt(self, data: schemas.RefreshJWT) -> core_schemas.JWT:
        ...

    async def forgot_password(self, data: dict) -> None:
        ...

    async def reset_password(self, data: dict) -> None:
        ...

    async def change_password(self, data: dict) -> None:
        ...

    async def change_email_session(self, user: dict, data: dict) -> core_schemas.Session:
        ...

    async def change_email(self, data: dict) -> None:
        ...


class UserServiceV1(NamedTuple):
    repo: repos.UserRepoInterface
    redis: aioredis.Redis

    async def create_user_session(self, data: schemas.CreateUser) -> core_schemas.Session:
        return await self._create_session(data.model_dump())

    async def create_user(self, data: core_schemas.CreateSession) -> models.User:
        raw_data = await self.redis.get(
            constants.USER_SESSION_KEY.format(data.session_id)
        )

        if not raw_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Сессия истекла или не найдена"
            )

        session = json.loads(raw_data)

        if session.get("code") != data.code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный код подтверждения"
            )

        await self.redis.delete(
            constants.USER_SESSION_KEY.format(data.session_id)
        )

        session_data = session.get("data", {})
        session_data["password"] = utils.hash_password(
            session_data.get("password", "")
        )

        user = schemas.CreateUser(**session_data)

        return await self.repo.create_user(user)

    async def update_user(self, user_id: uuid.UUID, data: schemas.UpdateUser) -> models.User:
        return await self.repo.update_user(
            filter_kwargs={'id': user_id}, **data.model_dump(exclude_unset=True),
        )

    async def get_user(self, user_id: uuid.UUID) -> models.User:
        return await self.repo.get_user(id=user_id)

    async def get_users(
            self, page: int, page_size: int, filters: tuple = ()
    ) -> core_schemas.PaginatedResponse[schemas.ListUser]:
        return await self.repo.get_users(page=page, page_size=page_size, filters=filters)

    async def create_jwt(self, data: schemas.CreateJWT) -> core_schemas.JWT:
        user_db = await self.repo.get_user(verify_password=True, **data.model_dump())
        user = schemas.User.model_validate(user_db)
        payload = {'user': json.loads(user.model_dump_json())}

        return utils.create_jwt(payload)

    async def refresh_jwt(self, data: schemas.RefreshJWT) -> core_schemas.JWT | JSONResponse:
        try:
            decoded_token = jwt.decode(data.refresh, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return JSONResponse(status_code=401, content="Token has expired")
        except jwt.InvalidTokenError:
            return JSONResponse(status_code=401, content="Invalid token")

        payload = {'user': decoded_token.get("user")}
        return utils.create_jwt(payload)

    async def _create_session(self, data):
        session_id = uuid.uuid4()
        code = utils.generate_code()
        payload = json.dumps({'code': code, 'data': data})
        await email_service.send_email(
            to_email=data["email"],
            subject="Подтверждение регистрации",
            html=f"""
            <h2>Код подтверждения</h2>
            <p>Ваш код: <b>{code}</b></p>
            """
        )
        await self.redis.setex(
            constants.USER_SESSION_KEY.format(session_id),
            constants.USER_SESSION_KEY_TTL,
            payload,
        )

        return core_schemas.Session(session_id=session_id)

    async def forgot_password(self, data: dict) -> None:
        user = await self.repo.get_user_by_email(data["email"])

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Такой почты не существует"
            )

        token = str(uuid.uuid4())
        await self.redis.setex(
            constants.RESET_PASSWORD_KEY.format(token),
            constants.RESET_PASSWORD_TTL,
            str(user.id),
        )
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"

        await email_service.send_email(
            to_email=data["email"],
            subject="Восстановление пароля",
            html=f"""
                <h2>Восстановление пароля</h2>
                <p>Нажмите на ссылку ниже, чтобы задать новый пароль:</p>
                <p>
                    <a href="{reset_link}">
                        Восстановить пароль
                    </a>
                </p>
                <p>Ссылка действует 15 минут.</p>
            """
        )

    async def reset_password(self, data: dict) -> None:
        key = constants.RESET_PASSWORD_KEY.format(data["token"])

        user_id = await self.redis.get(key)

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ссылка недействительна или истекла"
            )

        user_id = uuid.UUID(user_id.decode())
        password = utils.hash_password(data["password"])
        await self.repo.update_user_password(
            user_id=user_id,
            password=password,
        )

        await self.redis.delete(key)

    async def change_password(self, user_id: uuid.UUID, data: dict) -> None:
        await self.repo.change_password(
            user_id=user_id,
            old_password=data["old_password"],
            new_password=data["new_password"],
        )

    async def change_email_session(self, user: dict, data: dict) -> core_schemas.Session:
        current_user = await self.repo.get_user(id=user.get('id'))
        if current_user.email == data.get('email'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Это уже ваша текущая почта"
            )

        exists = await self.repo.get_user_by_email(data.get('email'))

        if exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с такой почтой уже существует"
            )

        session_id = uuid.uuid4()
        code = utils.generate_code()

        payload = json.dumps({
            "code": code,
            "email": data.get('email'),
            "user_id": str(user.get('id')),
        })

        await self.redis.setex(
            constants.CHANGE_EMAIL_SESSION_KEY.format(session_id),
            constants.USER_SESSION_KEY_TTL,
            payload,
        )

        await email_service.send_email(
            to_email=data.get('email'),
            subject="Подтверждение смены почты",
            html=f"""
                    <h2>Подтверждение смены почты</h2>

                    <p>Ваш код подтверждения:</p>

                    <h1>{code}</h1>

                    <p>Код действует 5 минут.</p>
                """
        )

        return core_schemas.Session(
            session_id=session_id
        )

    async def change_email(self, data: dict) -> None:
        raw_data = await self.redis.get(
            constants.CHANGE_EMAIL_SESSION_KEY.format(data["session_id"])
        )

        if not raw_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Сессия истекла или не найдена"
            )

        session = json.loads(raw_data)

        if session.get("code") != data["code"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный код подтверждения"
            )

        await self.repo.update_user(
            filter_kwargs={"id": uuid.UUID(session["user_id"])},
            email=session["email"],
        )

        await self.redis.delete(
            constants.CHANGE_EMAIL_SESSION_KEY.format(data["session_id"])
        )