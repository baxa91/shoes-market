import uuid

from sqlalchemy import String, Text, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shoes_market import models


ProductTag = Table(
    'product_tag', models.Base.metadata,
    Column('product_id', ForeignKey('products_product.id'), primary_key=True),
    Column('tag_id', ForeignKey('tags_tag.id'), primary_key=True)
)
Favorite = Table(
    'favorite_products', models.Base.metadata,
    Column('product_id', ForeignKey('products_product.id'), primary_key=True),
    Column('client_id', ForeignKey('users_user.id'), primary_key=True)
)


class Tag(models.BaseModel):
    __tablename__ = 'tags_tag'

    name: Mapped[str] = mapped_column(String(255), index=True, unique=True)
    products = relationship('Product', secondary=ProductTag, back_populates='tags')


class Product(models.BaseModel):
    __tablename__ = 'products_product'

    title: Mapped[str] = mapped_column(String(255))
    price: Mapped[int]
    currency: Mapped[str] = mapped_column(String(4), default='KZT')
    description: Mapped[str] = mapped_column(Text(), nullable=True)
    main_image: Mapped[str] = mapped_column(Text())
    is_active: Mapped[bool] = mapped_column(default=True)
    tags = relationship('Tag', secondary=ProductTag, back_populates='products', cascade='all')
    images = relationship('ProductImage', back_populates='products', cascade='all, delete-orphan')
    favorites = relationship(
        'User', secondary=Favorite, back_populates='favorites', cascade='all')
    orders = relationship('Order', back_populates='product', cascade='all, delete-orphan')

    repr_cols_num = 10


class ProductImage(models.BaseModel):
    __tablename__ = 'product_image'

    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('products_product.id', ondelete='CASCADE')
    )
    image: Mapped[str] = mapped_column(Text())
    products = relationship('Product', back_populates='images')
