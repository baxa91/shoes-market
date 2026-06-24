from fastapi import APIRouter, Depends, status
from shoes_market import connection, depends as core_depends
from . import handlers, repos, services, schemas


repo = repos.AboutUsRepoV1()
service = services.AboutUsServiceV1(repo=repo, redis=connection.Connection.aioredis())
handler = handlers.AboutUsHandler(service=service)
router = APIRouter(prefix='/about-us', tags=['about-us'])

router.add_api_route(
    '/', handler.create_about_us, methods=['post'], status_code=status.HTTP_201_CREATED
    # dependencies=[Depends(core_depends.is_admin)]
)
router.add_api_route('/', handler.get_about_us, methods=['get'])
router.add_api_route('/contact/', handler.get_contact_page, methods=['get'])
router.add_api_route(
    '/image/{pk}/', handler.delete_about_image, methods=['delete'],
    # dependencies=[Depends(core_depends.is_admin)]
)
router.add_api_route(
    '/', handler.update_about_us, methods=['patch'],
    # dependencies=[Depends(core_depends.is_admin)]
)
router.add_api_route(
    '/image/', handler.create_about_image, methods=['post'],
    # dependencies=[Depends(core_depends.is_admin)]
)
router.add_api_route(
    '/contact/', handler.update_contact_page, methods=['patch'],
    dependencies=[Depends(core_depends.is_admin)]
)
router.add_api_route(
    '/contact/', handler.create_contact_page, methods=['post'],
    # dependencies=[Depends(core_depends.is_admin)]
)
