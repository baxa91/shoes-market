from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from shoes_market import schemas


class PageNumberPagination:
    def __init__(self, session: AsyncSession, query: Select, page: int, page_size: int, schema):
        self.session = session
        self.query = query
        self.page = page
        self.page_size = page_size
        self.schema = schema

    async def get_response(self) -> schemas.PaginatedResponse:
        limit = self.page_size
        offset = (self.page - 1) * self.page_size

        query = self.query.limit(limit).offset(offset)
        count = await self._get_total_count()
        pages = self._get_number_of_pages(count)

        result = {
            'count': count,
            'pages': pages,
            'results': [self.schema.model_validate(i).model_dump()
                        for i in await self.session.scalars(query)]
            if self.schema else [i for i in await self.session.scalars(query)],
        }
        return schemas.PaginatedResponse(**result)

    def _get_number_of_pages(self, count: int) -> int:
        rest = count % self.page_size
        quotient = count // self.page_size

        return quotient if not rest else quotient + 1

    async def _get_total_count(self) -> int:
        return await self.session.scalar(select(func.count()).select_from(self.query.subquery()))


async def paginate(
        db_session, query: Select, page: int, page_size: int, schema=None
) -> schemas.PaginatedResponse:
    async with db_session as session:
        paginator = PageNumberPagination(session, query, page, page_size, schema)
        return await paginator.get_response()
