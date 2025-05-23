import datetime
import io
import os
import random
import uuid

import jwt
from PIL import Image

from passlib.handlers.pbkdf2 import pbkdf2_sha256
from shoes_market import settings, schemas
from shoes_market.products import exceptions


def generate_code(k: int = 6) -> str:
    if settings.DEBUG:
        return '4' * k

    return ''.join(random.choices('0123456789', k=k))


def create_jwt(
    payload: dict,
    access_ttl: int = settings.JWT_ACCESS_TTL,
    refresh_ttl: int = settings.JWT_REFRESH_TTL,
    secret: str = settings.SECRET_KEY
) -> schemas.JWT:
    now = datetime.datetime.utcnow()
    access_exp = now + datetime.timedelta(seconds=access_ttl)
    refresh_exp = now + datetime.timedelta(seconds=refresh_ttl)

    access = jwt.encode(
        payload={**payload, 'type': 'access', 'exp': access_exp},
        key=secret,
        algorithm='HS256'
    )
    refresh = jwt.encode(
        payload={**payload, 'type': 'refresh', 'exp': refresh_exp},
        key=secret,
        algorithm='HS256'
    )

    return schemas.JWT(access=access, refresh=refresh)


def hash_password(password: str) -> str:
    return pbkdf2_sha256.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    if not password:
        return False

    return pbkdf2_sha256.verify(password, hashed_password)


async def create_mediafile(path: str, file: bytes) -> str | None:
    if not file:
        return None

    file_name = f'{str(uuid.uuid4())}.webp'
    os.makedirs(f'{settings.MEDIA}{path}', exist_ok=True)
    file_path = f'{path}{file_name}'
    try:
        image = Image.open(io.BytesIO(file))
        image.save(f'{settings.MEDIA}{file_path}', format='WEBP')
        return file_path
    except Exception:
        raise exceptions.ImageTypeException
