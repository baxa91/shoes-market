import enum
import uuid

from sqlalchemy import Text, ForeignKey, Float, Column, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shoes_market import models


class OrderStatus(enum.Enum):
    NEW = "new"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELED = "canceled"


class Order(models.BaseModel):
    __tablename__ = 'orders_order'

    description: Mapped[str] = mapped_column(Text(), nullable=True)
    ankle: Mapped[float] = mapped_column(Float(), nullable=True)
    foot_length: Mapped[float] = mapped_column(Float())
    foot_width: Mapped[float] = mapped_column(Float(), nullable=True)
    client_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('users_user.id', ondelete='CASCADE')
    )
    status = Column(Enum(OrderStatus), default=OrderStatus.PROCESSING)
    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('products_product.id', ondelete='CASCADE')
    )
    product = relationship('Product', back_populates='orders')
    client = relationship('User', back_populates='orders')

    repr_cols_num = 10
