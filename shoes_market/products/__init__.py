from fastapi import APIRouter

from shoes_market import database, connection

from . import handlers, repos, services, schemas


repo = repos.ProductRepoV1(db_session=database.async_session())
service = services.ProductServiceV1(repo=repo, redis=connection.Connection.aioredis())
handler = handlers.ProductHandler(service=service)
router = APIRouter(prefix='/products', tags=['products'])

router.add_api_route(
    '/', handler.create_product, methods=['post'], response_model=schemas.Product)
router.add_api_route('/tags/', handler.create_tag, methods=['post'])
router.add_api_route('/tags/', handler.get_tags)
router.add_api_route('/tags/{pk}/', handler.get_tag)
router.add_api_route('/tags/{pk}/', handler.update_tag, methods=['patch'])
router.add_api_route('/tags/{pk}/', handler.delete_tag, methods=['delete'])
