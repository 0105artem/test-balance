from contextlib import asynccontextmanager

from loguru import logger
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.config import Config

SQLALCHEMY_DATABASE_URL = Config.DATABASE_URI


engine = create_async_engine(SQLALCHEMY_DATABASE_URL, future=True, echo=False)
AsyncLocalSession = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()


@asynccontextmanager
async def get_async_session():
    session = AsyncLocalSession()
    try:
        yield session
    except Exception as e:
        logger.error(e)
        await session.rollback()
    finally:
        await session.close()


def async_session(func):
    async def wrapper(*args, **kwargs):
        async with get_async_session() as session:
            return await func(session, *args, **kwargs)
    return wrapper
