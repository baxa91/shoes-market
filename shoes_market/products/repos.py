import base64
import os
import uuid
from typing import NamedTuple, Protocol, NoReturn

from sqlalchemy import insert, select, delete, update, desc, asc, exists
from sqlalchemy.orm import joinedload, selectinload

from shoes_market import utils, pagination, schemas as core_schemas, settings, database

from . import models, schemas


class ProductRepoInterface(Protocol):

    @staticmethod
    async def create_tag(data: schemas.CreateTag) -> models.Tag:
        ...

    @staticmethod
    async def get_tag(filters: tuple = ()) -> models.Tag:
        ...

    @staticmethod
    async def get_tags() -> list[schemas.Tag]:
        ...

    @staticmethod
    async def update_tag(filters: tuple, data: schemas.CreateTag) -> schemas.Tag:
        ...

    @staticmethod
    async def delete_tag(filters: tuple = ()) -> NoReturn:
        ...

    @staticmethod
    async def create_product(data: schemas.CreateProduct) -> models.Product:
        ...

    @staticmethod
    async def get_products(
            page: int, page_size: int, filters1,
            order_by: bool | None, user_id: uuid.UUID = None, like: bool = False
    ) -> core_schemas.PaginatedResponse[schemas.ListProduct]:
        ...

    @staticmethod
    async def get_product(filters: tuple = ()) -> schemas.DetailProduct:
        ...

    @staticmethod
    async def delete_product(pk: uuid.UUID) -> NoReturn:
        ...

    @staticmethod
    async def update_product(pk: uuid.UUID, data: schemas.UpdateProduct) -> schemas.Product:
        ...

    @staticmethod
    async def create_product_image(data: schemas.CreateProductImage) -> schemas.ProductImage:
        ...

    @staticmethod
    async def delete_product_image(filters: tuple = ()) -> NoReturn:
        ...

    @staticmethod
    async def like_dislike_product(**kwargs) -> None:
        ...


class ProductRepoV1(NamedTuple):

    @staticmethod
    async def create_tag(data: schemas.CreateTag) -> models.Tag:
        return await models.Tag.create(db_session=database.async_session(), data=data.model_dump())

    @staticmethod
    async def get_tag(filters: tuple = ()) -> models.Tag:
        return await models.Tag.get(db_session=database.async_session(), filters=filters)

    @staticmethod
    async def get_tags() -> list[schemas.Tag]:
        async with database.async_session() as session:
            query = await session.scalars(select(models.Tag))
            result = query.all()

        return result

    @staticmethod
    async def update_tag(filters: tuple, data: schemas.CreateTag) -> schemas.Tag:
        await models.Tag.update(
            db_session=database.async_session(), filters=filters, data=data.model_dump())

        return await models.Tag.get(db_session=database.async_session(), filters=filters)

    @staticmethod
    async def delete_tag(filters: tuple = ()) -> NoReturn:
        await models.Tag.delete(database.async_session(), filters)

    @staticmethod
    async def create_product(data: schemas.CreateProduct) -> models.Product:
        data_dict = data.model_dump()
        tag_dict = data_dict.pop('tags')
        main_image = data_dict.pop('main_image')
        async with database.async_session() as session:
            file = base64.b64decode(main_image)
            file_path = await utils.create_mediafile('products/', file)
            data_dict['main_image'] = file_path
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
            product = await session.scalars(
                select(models.Product).options(
                    joinedload(models.Product.tags)
                ).filter(
                    models.Product.id == product.id)
            )
            session.expunge_all()
            await session.commit()

        return product.first()

    @staticmethod
    async def get_products(
            page: int, page_size: int, filters,
            order_by: bool | None, user_id: uuid.UUID = None, like: bool = False
    ) -> core_schemas.PaginatedResponse[schemas.ListProduct]:
        def base_query():
            query = select(models.Product).where(filters).options(
                selectinload(models.Product.tags), selectinload(models.Product.images),
                selectinload(models.Product.favorites))
            if like:
                query = query.join(
                    models.Favorite, models.Favorite.c.product_id == models.Product.id)
            return query

        query = base_query()

        if order_by is not None:
            sort_order = desc(models.Product.price) if order_by else asc(models.Product.price)
            query = query.order_by(sort_order, desc(models.Product.created_at))
        else:
            query = query.order_by(desc(models.Product.created_at))

        return await pagination.paginate(
            database.async_session(), query,
            page, page_size, schemas.ListProduct, **{'user_id': user_id}
        )

    @staticmethod
    async def get_product(filters: tuple = ()) -> schemas.DetailProduct:
        return await models.Product.get(database.async_session(), filters, *['tags', 'images'])

    @staticmethod
    async def delete_product(pk: uuid.UUID) -> NoReturn:
        async with database.async_session() as session, session.begin():
            rows = await session.scalars(
                select(models.ProductImage).where(models.ProductImage.product_id == pk)
            )
            row = rows.all()
            for image in row:
                os.remove(f'{settings.MEDIA}{image.image}')

            query = delete(models.Product).where(models.Product.id == pk)
            await session.execute(query)
            await session.commit()

    @staticmethod
    async def update_product(pk: uuid.UUID, data: schemas.UpdateProduct) -> schemas.Product:
        product_dict = data.model_dump(exclude_unset=True)
        async with database.async_session() as session, session.begin():
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
            if product_dict.get('main_image'):
                file = base64.b64decode(product_dict.get('main_image'))
                file_path = await utils.create_mediafile('products/', file)
                product_dict['main_image'] = file_path
                if product_dict.get('old_main_image'):
                    os.remove(f'{settings.MEDIA}{product_dict.get("old_main_image")}')
                    del product_dict['old_main_image']

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

    @staticmethod
    async def create_product_image(data: schemas.CreateProductImage) -> schemas.ProductImage:
        async with database.async_session() as session, session.begin():
            image_dict = {'product_id': data.product_id}
            file = base64.b64decode(data.image)
            file_path = await utils.create_mediafile('products/', file)
            image_dict['image'] = file_path
            rows = await session.scalars(
                insert(models.ProductImage).returning(models.ProductImage).values(**image_dict)
            )
            row = rows.one()
            session.expunge_all()
            await session.commit()

        return row

    @staticmethod
    async def delete_product_image(filters: tuple = ()) -> NoReturn:
        await models.ProductImage.delete(database.async_session(), filters)

    @staticmethod
    async def like_dislike_product(**kwargs) -> None:
        fields = [getattr(models.Favorite.c, field) == value for field, value in kwargs.items()]
        query = select(exists().where(*fields))
        async with database.async_session() as session, session.begin():
            result = await session.execute(query)
            if not result.scalar():
                await session.execute(insert(models.Favorite).values([kwargs]))
            else:
                del_query = delete(models.Favorite).where(*fields)
                await session.execute(del_query)
            await session.commit()
