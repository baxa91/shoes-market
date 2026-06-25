import uuid
from pydantic import BaseModel, ConfigDict


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
