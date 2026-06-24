import uuid
from sqlalchemy import DateTime, Enum, String, Text, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from shoes_market.models import BaseModel


class AboutUs(BaseModel):
    __tablename__ = "about_us"

    title: Mapped[str] = mapped_column(String(255))
    subtitle: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content: Mapped[str] = mapped_column(Text())

    images: Mapped[list["AboutImage"]] = relationship(
        back_populates="about",
        cascade="all, delete-orphan",
        order_by="AboutImage.sort_order",
    )


class AboutImage(BaseModel):
    __tablename__ = "about_images"

    about_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("about_us.id", ondelete="CASCADE"),
        nullable=False,
    )

    image: Mapped[str] = mapped_column(Text())
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    about: Mapped["AboutUs"] = relationship(
        back_populates="images"
    )


class ContactPage(BaseModel):
    __tablename__ = "contact_pages"

    instagram: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    map_url: Mapped[str | None] = mapped_column(Text(), nullable=True)
    work_hours: Mapped[str | None] = mapped_column(String(255), nullable=True)

    phones: Mapped[list["ContactPhone"]] = relationship(
        back_populates="contact_page",
        cascade="all, delete-orphan",
        order_by="ContactPhone.sort_order"
    )


class ContactPhone(BaseModel):
    __tablename__ = "contact_phones"

    contact_page_id: Mapped[str] = mapped_column(
        ForeignKey("contact_pages.id", ondelete="CASCADE")
    )

    phone: Mapped[str] = mapped_column(String(50))
    title: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_whatsapp: Mapped[bool] = mapped_column(default=False)
    sort_order: Mapped[int] = mapped_column(default=0)

    contact_page: Mapped["ContactPage"] = relationship(
        back_populates="phones"
    )
