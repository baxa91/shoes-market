from typing import NoReturn

from redis import asyncio as aioredis, client, utils
from shoes_market import exceptions, settings


class Connection:
    __redis: client.Redis = None
    __aioredis: aioredis.Redis = None

    @classmethod
    def redis(cls) -> client.Redis | NoReturn:
        if redis_url := settings.REDIS_URL:
            cls.__redis = utils.from_url(redis_url)
            return cls.__redis

        raise exceptions.RedisUrlNotFound

    @classmethod
    def aioredis(cls) -> aioredis.Redis | NoReturn:
        if redis_url := settings.REDIS_URL:
            cls.__aioredis = aioredis.from_url(redis_url)
            return cls.__aioredis

        raise exceptions.RedisUrlNotFound

    @classmethod
    def close_redis(cls) -> None:
        if not cls.__redis:
            return None

        cls.__redis.close()

    @classmethod
    async def close_aioredis(cls) -> None:
        if not cls.__aioredis:
            return None

        await cls.__aioredis.close()
