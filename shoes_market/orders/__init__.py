from fastapi import APIRouter, Depends

from shoes_market import depends as core_depends

from . import handlers, repos, services, schemas


repo = repos.OrderRepoV1()
service = services.OrderServiceV1(repo=repo)
handler = handlers.OrderHandler(service=service)
router = APIRouter(prefix='/orders', tags=['orders'])

router.add_api_route(
    '/', handler.create_order, methods=['post'], response_model=schemas.Order,
    dependencies=[Depends(core_depends.is_authenticated)]
)
router.add_api_route(
    '/', handler.get_orders, methods=['get'],
    dependencies=[Depends(core_depends.is_admin)]
)
