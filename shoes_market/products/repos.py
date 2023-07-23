import base64
from typing import NamedTuple, Protocol, NoReturn

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from shoes_market import utils

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
