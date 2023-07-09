import json
import uuid
import jwt
from typing import NamedTuple, Protocol

from fastapi.responses import JSONResponse
from redis import asyncio as aioredis

from shoes_market import constants, schemas as core_schemas, utils, settings

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


class UserServiceV1(NamedTuple):
    repo: repos.UserRepoInterface
    redis: aioredis.Redis

    async def create_user_session(self, data: schemas.CreateUser) -> core_schemas.Session:
        return await self._create_session(data.model_dump())

    async def create_user(self, data: core_schemas.CreateSession) -> models.User:
        data = await self.redis.getdel(constants.USER_SESSION_KEY.format(data.session_id))
        session = json.loads(data)
        session_data = session.get('data', {})
        session_data['password'] = utils.hash_password(session_data.get('password', ''))
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

        await self.redis.setex(
            constants.USER_SESSION_KEY.format(session_id),
            constants.USER_SESSION_KEY_TTL,
            payload,
        )

        return core_schemas.Session(session_id=session_id)
