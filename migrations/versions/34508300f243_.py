"""empty message

Revision ID: 34508300f243
Revises: 307fde8c074d
Create Date: 2026-06-22 10:06:53.824094

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '34508300f243'
down_revision = '307fde8c074d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint(
        "favorite_products_client_id_fkey",
        "favorite_products",
        type_="foreignkey",
    )
    op.drop_constraint(
        "favorite_products_product_id_fkey",
        "favorite_products",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "favorite_products_client_id_fkey",
        "favorite_products",
        "users_user",
        ["client_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "favorite_products_product_id_fkey",
        "favorite_products",
        "products_product",
        ["product_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint(
        "product_tag_tag_id_fkey",
        "product_tag",
        type_="foreignkey",
    )
    op.drop_constraint(
        "product_tag_product_id_fkey",
        "product_tag",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "product_tag_tag_id_fkey",
        "product_tag",
        "tags_tag",
        ["tag_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "product_tag_product_id_fkey",
        "product_tag",
        "products_product",
        ["product_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        "product_tag_product_id_fkey",
        "product_tag",
        type_="foreignkey",
    )
    op.drop_constraint(
        "product_tag_tag_id_fkey",
        "product_tag",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "product_tag_product_id_fkey",
        "product_tag",
        "products_product",
        ["product_id"],
        ["id"],
    )
    op.create_foreign_key(
        "product_tag_tag_id_fkey",
        "product_tag",
        "tags_tag",
        ["tag_id"],
        ["id"],
    )

    op.drop_constraint(
        "favorite_products_product_id_fkey",
        "favorite_products",
        type_="foreignkey",
    )
    op.drop_constraint(
        "favorite_products_client_id_fkey",
        "favorite_products",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "favorite_products_product_id_fkey",
        "favorite_products",
        "products_product",
        ["product_id"],
        ["id"],
    )
    op.create_foreign_key(
        "favorite_products_client_id_fkey",
        "favorite_products",
        "users_user",
        ["client_id"],
        ["id"],
    )
