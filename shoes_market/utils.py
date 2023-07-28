import datetime
import os
import random
import re

import jwt

from passlib.handlers.pbkdf2 import pbkdf2_sha256
from shoes_market import settings, schemas


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


async def create_mediafile(path: str, name: str, file: bytes) -> str:
    os.makedirs(f'{settings.MEDIA}{path}', exist_ok=True)
    file_name = await get_unique_name(path, name)
    file_path = os.path.join(f'{settings.MEDIA}{path}', file_name)
    with open(file_path, 'wb') as f:
        f.write(file)

    return f'{path}{file_name}'


async def get_unique_name(path: str, name: str, count=1) -> str:
    file_path = os.path.join(f'{settings.MEDIA}{path}', name)
    if os.path.exists(file_path):
        count = count + 1
        split_name = name.rsplit('.', 1)
        match = re.search(r'\((\d+)\)', split_name[0])
        if match:
            new_name = f'{split_name[0].replace(match.group(1), str(count))}.{split_name[1]}'
        else:
            new_name = f'{split_name[0]}({count}).{split_name[1]}'

        return await get_unique_name(path, new_name, count)
    else:
        return name
