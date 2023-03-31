from aiohttp import web

from app.db.config import Base


async def init_db(app: web.Application):
    async with app['db'].begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
