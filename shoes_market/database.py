from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker
from shoes_market import settings


async_engine = create_async_engine(
    settings.DATABASE_URL.replace('postgresql', 'postgresql+asyncpg'),
)
async_session = async_sessionmaker(async_engine)

engine = create_engine(settings.DATABASE_URL.replace('postgresql', 'postgresql+psycopg'))
session = sessionmaker(engine)
