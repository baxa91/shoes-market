import uuid

from sqlalchemy import String, Text, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from shoes_market import models


class Tag(models.BaseModel):
    __tablename__ = 'tags_tag'
    name: Mapped[str] = mapped_column(String(255), index=True)


class Product(models.BaseModel):
    __tablename__ = 'products_product'

    title: Mapped[str] = mapped_column(String(255))
    price: Mapped[int] = mapped_column(Integer())
    currency: Mapped[str] = mapped_column(String(4), default='KZT')
    description: Mapped[str] = mapped_column(Text(), nullable=True)


class ProductTag(models.Base):
    __tablename__ = 'product_tag'

    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('products_product.id'))
    tag_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('tags_tag.id'))


class ProductImage(models.BaseModel):
    __tablename__ = 'product_image'

    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('products_product.id'))
    image: Mapped[str] = mapped_column(Text())
    is_base: Mapped[bool] = mapped_column(default=False)
