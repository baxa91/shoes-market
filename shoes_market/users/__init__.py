from fastapi import APIRouter, Depends, status

from shoes_market import database, connection, depends

from . import handlers, repos, services


repo = repos.UserRepoV1(db_session=database.async_session())
service = services.UserServiceV1(repo=repo, redis=connection.Connection.aioredis())
handler = handlers.UserHandler(service=service)
router = APIRouter(prefix='/users', tags=['users'])

router.add_api_route('/session/', handler.create_user_session, methods=['post'])
router.add_api_route('/jwt/', handler.create_jwt, methods=['post'])
router.add_api_route(
    '/jwt/refresh/',
    handler.refresh_jwt,
    methods=['post'],
    dependencies=[Depends(depends.is_authenticated)],
)
router.add_api_route('/', handler.get_users, methods=['get'])
router.add_api_route(
    '/', handler.create_user, methods=['post'], status_code=status.HTTP_201_CREATED,
)
router.add_api_route(
    '/me/', handler.get_user,
    methods=['get'],
    dependencies=[Depends(depends.is_authenticated)],
)
router.add_api_route(
    '/me/', handler.update_user,
    methods=['patch'],
    dependencies=[Depends(depends.is_authenticated)],
)
