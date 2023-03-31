import json

import pydantic
from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from sqlalchemy.orm import Session
from loguru import logger

from app.db.config import async_session
from app.db.dals.transaction_dal import TransactionDAL
from app.db.dals.user_dals import UserDAL
from app.schemas import user_schemas
from app.utils.json_encoders import DatetimeJsonEncoder


@async_session
async def create_user(session: Session, request: Request) -> Response:
    try:
        data = await request.json()

        user = user_schemas.UserBase(**data)
        user_DAL = UserDAL(session)
        new_user = await user_DAL.create_user(user)
        if new_user:
            new_user = user_schemas.UserDB(**new_user.__dict__)
            return web.json_response(new_user.dict(),
                                     dumps=lambda obj: json.dumps(obj, cls=DatetimeJsonEncoder),
                                     status=201)
        else:
            return web.json_response({"details": f"User {user.name} already exists!"}, status=403)

    except pydantic.ValidationError as e:
        logger.error(e)
        return web.json_response({'details': json.loads(e.json())}, status=422)

    except Exception as e:
        logger.error(e)
        return web.json_response({"details": "Failed to create user!"}, status=500)


@async_session
async def get_user(session: Session, request: Request) -> Response:
    try:
        date = request.query.get('date')

        if date:
            transaction_DAL = TransactionDAL(session)
            search_date = user_schemas.UserDate(date=date)
            balance = await transaction_DAL.get_nearest_transaction(search_date.date)
            if balance:
                return web.json_response({"balance": str(balance)}, status=200)
        user_id = user_schemas.UserId(id=request.match_info.get('id')).id
        user_DAL = UserDAL(session)
        user = await user_DAL.get_user(user_id)

        if user is not None:
            user = user_schemas.UserDB(**user.__dict__)
            return web.json_response(user.dict(),
                                     dumps=lambda obj: json.dumps(obj, cls=DatetimeJsonEncoder),
                                     status=200)
        else:
            return web.json_response({"details": f"User {user_id} was not found!"}, status=404)

    except pydantic.ValidationError as e:
        logger.error(e)
        return web.json_response({'details': json.loads(e.json())}, status=422)

    except Exception as e:
        logger.error(e)
        return web.json_response({"details": "Failed to get user balance!"}, status=500)
