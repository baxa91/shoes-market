from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession


class PageNumberPagination:
    def __init__(self, session: AsyncSession, query: Select, page: int, page_size: int):
        self.session = session
        self.query = query
        self.page = page
        self.page_size = page_size

    async def get_response(self) -> dict:
        limit = self.page_size
        offset = (self.page - 1) * self.page_size

        query = self.query.limit(limit).offset(offset)
        count = await self._get_total_count()
        pages = self._get_number_of_pages(count)

        return {
            'count': count,
            'pages': pages,
            'results': [i for i in await self.session.scalars(query)],
        }

    def _get_number_of_pages(self, count: int) -> int:
        rest = count % self.page_size
        quotient = count // self.page_size

        return quotient if not rest else quotient + 1

    async def _get_total_count(self) -> int:
        return await self.session.scalar(select(func.count()).select_from(self.query.subquery()))


async def paginate(db_session, query: Select, page: int, page_size: int) -> dict:
    async with db_session as session:
        paginator = PageNumberPagination(session, query, page, page_size)
        return await paginator.get_response()
