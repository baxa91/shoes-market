import datetime
import random
import uuid
import base64
import boto3
import jwt
from PIL import Image
from io import BytesIO
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from shoes_market import settings, schemas
from urllib.parse import urlparse, unquote
from botocore.client import Config


def generate_code(k: int = 6) -> str:
    return ''.join(random.choices('0123456789', k=k))


def create_jwt(
    payload: dict,
    access_ttl: int = settings.JWT_ACCESS_TTL,
    refresh_ttl: int = settings.JWT_REFRESH_TTL,
    secret: str = settings.SECRET_KEY
) -> schemas.JWT:
    now = datetime.datetime.now(datetime.UTC)
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


class R2StorageService:
    def __init__(self):
        self.bucket = settings.R2_BUCKET_NAME
        self.public_url = settings.R2_PUBLIC_URL.rstrip("/")

        self.client = boto3.client(
            "s3",
            endpoint_url=f"https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
            aws_access_key_id=settings.R2_ACCESS_KEY_ID,
            aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
            config=Config(signature_version="s3v4"),
            region_name="auto",
        )

    async def upload_base64_image(
        self,
        base64_image: str,
        folder: str,
        quality: int = 80,
    ) -> str:
        folder = folder.strip("/")

        image_bytes = self._decode_base64_image(base64_image)

        image = Image.open(BytesIO(image_bytes))
        image = image.convert("RGB")

        output = BytesIO()
        image.save(
            output,
            format="WEBP",
            quality=quality,
            method=6,
            optimize=True,
        )
        output.seek(0)

        key = f"{folder}/{uuid.uuid4()}.webp"

        self.client.upload_fileobj(
            output,
            self.bucket,
            key,
            ExtraArgs={
                "ContentType": "image/webp",
                "CacheControl": "public, max-age=31536000",
            },
        )

        return f"{self.public_url}/{key}"

    def delete_file_by_url(self, url: str) -> None:
        key = self._extract_key_from_url(url)

        self.client.delete_object(
            Bucket=self.bucket,
            Key=key,
        )

    @staticmethod
    def _decode_base64_image(base64_image: str) -> bytes:
        if isinstance(base64_image, bytes):
            base64_image = base64_image.decode()

        if "," in base64_image:
            base64_image = base64_image.split(",", 1)[1]

        return base64.b64decode(base64_image)

    @staticmethod
    def _extract_key_from_url(url: str) -> str:
        parsed = urlparse(url)
        key = unquote(parsed.path.lstrip("/"))

        if not key:
            raise ValueError("Не удалось получить key из URL")

        return key


storage = R2StorageService()