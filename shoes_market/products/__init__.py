from fastapi import APIRouter, Depends

from shoes_market import database, connection, depends as core_depends

from . import handlers, repos, services, schemas


repo = repos.ProductRepoV1(db_session=database.async_session())
service = services.ProductServiceV1(repo=repo, redis=connection.Connection.aioredis())
handler = handlers.ProductHandler(service=service)
router = APIRouter(prefix='/products', tags=['products'])

router.add_api_route(
    '/', handler.create_product, methods=['post'], response_model=schemas.Product,
    dependencies=[Depends(core_depends.is_admin)]
)
router.add_api_route('/', handler.get_products, methods=['get'])
router.add_api_route('/tags/', handler.get_tags, methods=['get'])
router.add_api_route('/{pk}/', handler.get_product, methods=['get'])
router.add_api_route(
    '/{pk}/', handler.delete_product, methods=['delete'],
    dependencies=[Depends(core_depends.is_admin)]
)
router.add_api_route(
    '/{pk}/', handler.update_product, methods=['patch'],
    dependencies=[Depends(core_depends.is_admin)]
)
router.add_api_route(
    '/tags/', handler.create_tag, methods=['post'],
    dependencies=[Depends(core_depends.is_admin)]
)
router.add_api_route('/tags/{pk}/', handler.get_tag)
router.add_api_route(
    '/tags/{pk}/', handler.update_tag, methods=['patch'],
    dependencies=[Depends(core_depends.is_admin)]
)
router.add_api_route(
    '/tags/{pk}/', handler.delete_tag, methods=['delete'],
    dependencies=[Depends(core_depends.is_admin)]
)
router.add_api_route(
    '/image/{pk}/', handler.create_product_image, methods=['post'],
    dependencies=[Depends(core_depends.is_admin)]
)
router.add_api_route(
    '/image/{pk}/', handler.update_product_image, methods=['patch'],
    dependencies=[Depends(core_depends.is_admin)]
)
router.add_api_route(
    '/image/{pk}/', handler.delete_product_image, methods=['delete'],
    dependencies=[Depends(core_depends.is_admin)]
)
