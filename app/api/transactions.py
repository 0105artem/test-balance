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
from app.schemas import transaction_schemas
from app.utils.json_encoders import DatetimeJsonEncoder


@async_session
async def add_transaction(session: Session, request: Request) -> Response:
    try:
        data = await request.json()

        transaction = transaction_schemas.TransactionBase(**data)
        transaction_DAL = TransactionDAL(session)
        # Check if the transaction does not exist
        if await transaction_DAL.get_transaction(transaction.uid):
            return web.json_response({"details": f"Transaction {transaction.uid} already exists!"}, status=200)

        user_DAL = UserDAL(session)
        balance = await user_DAL.get_balance(transaction.user_id)
        # Check if user exists
        if balance is None:
            return web.json_response({"details": f"User {transaction.user_id} was not found!"}, status=404)

        if transaction.type == "DEPOSIT":
            new_balance = float(balance) + transaction.amount
            transaction = transaction.dict()
            transaction['new_balance'] = new_balance
            new_transaction = await transaction_DAL.create_transaction(transaction)
            if new_transaction:
                await user_DAL.change_balance(transaction['user_id'], new_balance)

                new_transaction = transaction_schemas.TransactionDB(**new_transaction.__dict__)
                return web.json_response(new_transaction.dict(),
                                         dumps=lambda obj: json.dumps(obj, cls=DatetimeJsonEncoder),
                                         status=200)
            else:
                return web.json_response({"details": "Transaction failed!"}, status=500)

        elif transaction.type == "WITHDRAW":
            new_balance = float(balance) - transaction.amount

            # Check if user has enough money to withdraw
            if new_balance < 0:
                return web.json_response({"details": f"Insufficient funds"}, status=402)

            transaction = transaction.dict()
            transaction['new_balance'] = new_balance
            new_transaction = await transaction_DAL.create_transaction(transaction)
            if new_transaction:
                await user_DAL.change_balance(transaction['user_id'], new_balance)

                new_transaction = transaction_schemas.TransactionDB(**new_transaction.__dict__)
                return web.json_response(new_transaction.dict(),
                                         dumps=lambda obj: json.dumps(obj, cls=DatetimeJsonEncoder),
                                         status=200)
            else:
                return web.json_response({"details": "Transaction failed!"}, status=500)
        else:
            return web.json_response({'details': 'Unknown type of transaction!'}, status=422)

    except pydantic.ValidationError as e:
        logger.error(e)
        return web.json_response({'details': json.loads(e.json())}, status=422)

    except Exception as e:
        logger.error(e)
        return web.json_response({"details": "Transaction failed!"}, status=500)


@async_session
async def get_transaction(session: Session, request: Request) -> Response:
    try:
        transaction_id = transaction_schemas.TransactionId(uid=request.match_info.get('id')).uid
        transaction_DAL = TransactionDAL(session)
        transaction = await transaction_DAL.get_transaction(transaction_id)

        if transaction is not None:
            transaction = transaction_schemas.TransactionDB(**transaction.__dict__)
            return web.json_response(transaction.dict(),
                                     dumps=lambda obj: json.dumps(obj, cls=DatetimeJsonEncoder),
                                     status=200)
        else:
            return web.json_response({"details": f"Transaction {transaction_id} was not found!"}, status=404)

    except pydantic.ValidationError as e:
        logger.error(e)
        return web.json_response({'details': json.loads(e.json())}, status=422)

    except Exception as e:
        logger.error(e)
        return web.json_response({"details": "Failed to get transaction!"}, status=500)
