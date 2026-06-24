import uuid
from shoes_market import settings
from urllib.parse import urljoin
from pydantic import BaseModel, ConfigDict, field_serializer


class CreateAboutUs(BaseModel):

    title: str
    subtitle: str | None = None
    content: str


class UpdateAboutUs(BaseModel):

    title: str | None = None
    subtitle: str | None = None
    content: str | None = None


class AboutImage(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    image: str
    sort_order: int

    @field_serializer('image')
    def serialize_image(self, image: str):
        if not image:
            return None

        return urljoin(settings.MEDIA_URL, image)


class CreateAboutImage(BaseModel):

    image: bytes
    sort_order: int


class AboutUs(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    subtitle: str | None = None
    content: str
    images: list[AboutImage]


class ContactPhone(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    phone: str
    title: str | None = None
    is_whatsapp: bool = False
    sort_order: int


class CreateContactPage(BaseModel):

    instagram: str | None = None
    address: str | None = None
    map_url: str | None = None
    work_hours: str | None = None
    phones: list[ContactPhone] = []


class ContactPage(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    instagram: str | None = None
    address: str | None = None
    map_url: str | None = None
    work_hours: str | None = None
    phones: list[ContactPhone]
