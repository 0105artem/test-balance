from aiohttp import web

from app.db.config import engine
from app.api import users, transactions

app = web.Application()
app['db'] = engine


def add_routes(app):
    app.router.add_route('POST', r'/v1/user', users.create_user, name='create_user')
    app.router.add_route('GET', r'/v1/user/{id}', users.get_user, name='get_user')
    app.router.add_route('POST', r'/v1/transaction', transactions.add_transaction, name='add_transaction')
    app.router.add_route('GET', r'/v1/transaction/{id}', transactions.get_transaction, name='incoming_transaction')


def init_app() -> web.Application:
    from .config import Config
    from .cleanups import close_db
    from .startups import init_db

    app['config'] = Config()
    app['db'] = engine

    # Startups
    app.on_startup.append(init_db)

    # Cleanups
    app.on_cleanup.append(close_db)
    add_routes(app)

    return app
