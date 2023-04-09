import json

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.json_encoders import DatetimeJsonEncoder
from app.models.user import UserModel
from app.schemas.user_schemas import UserId


async def create_user(request: Request) -> Response:
    data: dict = await request.json()
    session: AsyncSession = request["session"]
    user = UserModel(**data)

    new_user = await user.create_user(session)

    return web.json_response(dumps=lambda obj: json.dumps(obj, cls=DatetimeJsonEncoder),
                             data=new_user, status=201)


async def get_user(request: Request) -> Response:
    session: AsyncSession = request["session"]
    user_id = request.match_info['id']

    user = await UserModel.get_user(session, user_id)

    return web.json_response(dumps=lambda obj: json.dumps(obj, cls=DatetimeJsonEncoder),
                             data=user, status=200)


async def get_user_balance(request: Request) -> Response:
    session: AsyncSession = request["session"]
    date = request.query.get('date')
    user_id = request.match_info['id']
    # User id validation
    user_id = UserId(id=user_id).id

    await UserModel.check_user_exists(session, user_id)

    balance = await UserModel.get_balance(session, user_id, date=date)

    return web.json_response({"balance": str(balance)}, status=200)

