import base64
import os
import uuid
from typing import NamedTuple, Protocol, NoReturn

from sqlalchemy import insert, select, delete, update, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from shoes_market import utils, pagination, schemas as core_schemas, settings

from . import models, schemas


class ProductRepoInterface(Protocol):

    async def create_tag(self, data: schemas.CreateTag) -> models.Tag:
        ...

    async def get_tag(self, filters: tuple = ()) -> models.Tag:
        ...

    async def get_tags(self) -> list[schemas.Tag]:
        ...

    async def update_tag(self, filters: tuple, data: schemas.CreateTag) -> schemas.Tag:
        ...

    async def delete_tag(self, filters: tuple = ()) -> NoReturn:
        ...

    async def create_product(self, data: schemas.CreateProduct) -> models.Product:
        ...

    async def get_products(
            self, page: int, page_size: int, filters
    ) -> core_schemas.PaginatedResponse[schemas.Product]:
        ...

    async def get_product(self, filters: tuple = ()) -> schemas.Product:
        ...

    async def delete_product(self, pk: uuid.UUID) -> NoReturn:
        ...

    async def update_product(self, pk: uuid.UUID, data: schemas.UpdateProduct) -> schemas.Product:
        ...


class ProductRepoV1(NamedTuple):
    db_session: AsyncSession

    async def create_tag(self, data: schemas.CreateTag) -> models.Tag:
        return await models.Tag.create(db_session=self.db_session, data=data.model_dump())

    async def get_tag(self, filters: tuple = ()) -> models.Tag:
        return await models.Tag.get(db_session=self.db_session, filters=filters)

    async def get_tags(self) -> list[schemas.Tag]:
        async with self.db_session as session:
            query = await session.scalars(select(models.Tag))
            result = query.all()

        return result

    async def update_tag(self, filters: tuple, data: schemas.CreateTag) -> schemas.Tag:
        await models.Tag.update(
            db_session=self.db_session, filters=filters, data=data.model_dump())

        return await models.Tag.get(db_session=self.db_session, filters=filters)

    async def delete_tag(self, filters: tuple = ()) -> NoReturn:
        await models.Tag.delete(self.db_session, filters)

    async def create_product(self, data: schemas.CreateProduct) -> models.Product:
        data_dict = data.model_dump()
        tag_dict = data_dict.pop('tags')
        images_list = data_dict.pop('images')
        async with self.db_session as session:
            rows = await session.scalars(
                insert(models.Product).returning(models.Product).values(**data_dict)
            )
            product = rows.one()
            tag_list = []
            for tag in tag_dict:
                tag_list.append({
                    'product_id': product.id,
                    'tag_id': tag
                })

            await session.execute(insert(models.ProductTag).values(tag_list))
            product_images = []
            for image in images_list:
                image_dict = {'product_id': product.id, 'is_base': image['is_base']}
                file = base64.b64decode(image['image'])
                file_path = await utils.create_mediafile('products/', image['filename'], file)
                image_dict['image'] = file_path
                product_images.append(image_dict)

            await session.execute(insert(models.ProductImage).values(product_images))
            product = await session.scalars(
                select(models.Product).options(
                    joinedload(models.Product.tags), joinedload(models.Product.images)
                ).filter(
                    models.Product.id == product.id)
            )
            session.expunge_all()
            await session.commit()

        return product.first()

    async def get_products(
            self, page: int, page_size: int, filters
    ) -> core_schemas.PaginatedResponse[schemas.Product]:
        return await pagination.paginate(
            self.db_session, select(models.Product).where(filters).order_by(
                desc(models.Product.created_at)).options(
                selectinload(models.Product.tags), selectinload(models.Product.images)
            ),
            page, page_size, schemas.Product
        )

    async def get_product(self, filters: tuple = ()) -> schemas.Product:
        return await models.Product.get(self.db_session, filters, *['tags', 'images'])

    async def delete_product(self, pk: uuid.UUID) -> NoReturn:
        async with self.db_session as session, session.begin():
            rows = await session.scalars(
                select(models.ProductImage).where(models.ProductImage.product_id == pk)
            )
            row = rows.all()
            for image in row:
                os.remove(f'{settings.MEDIA}{image.image}')

            query = delete(models.Product).where(models.Product.id == pk)
            await session.execute(query)
            await session.commit()

    async def update_product(self, pk: uuid.UUID, data: schemas.UpdateProduct) -> schemas.Product:
        product_dict = data.model_dump(exclude_unset=True)
        async with self.db_session as session, session.begin():
            if product_dict.get('tags'):
                tags = product_dict.pop('tags')
                tag_list = []
                await session.execute(
                    delete(models.ProductTag).where(models.ProductTag.c.product_id == pk)
                )
                for tag in tags:
                    tag_list.append({
                        'product_id': pk,
                        'tag_id': tag
                    })

                await session.execute(insert(models.ProductTag).values(tag_list))

            if product_dict:
                query = update(models.Product).where(
                    models.Product.id == pk).values(**product_dict)
                await session.execute(query)

            product = await session.scalars(
                select(models.Product).options(
                    selectinload(models.Product.tags), selectinload(models.Product.images)
                ).filter(
                    models.Product.id == pk)
            )
            session.expunge_all()
            await session.commit()

        return product.one_or_none()
