import json

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import TransactionModel
from app.models.user import UserModel
from app.utils.json_encoders import DatetimeJsonEncoder


async def add_transaction(request: Request) -> Response:
    data: dict = await request.json()
    session: AsyncSession = request["session"]
    transaction = TransactionModel(**data)
    user_id = transaction.user_id

    # Check if transaction with same uuid exists in the database. If it does, then
    # raise TransactionAlreadyExists exception.
    await transaction.check_transaction_exists(session)

    # Get user balance from the database with blocking user for reading and writing.
    balance = await UserModel.get_balance(session, user_id, block=True)

    # Calculate new balance of the user based on the transaction type.
    new_balance = await transaction.calculate_balance(balance)

    # Insert transaction to the database and update balance of the user.
    new_transaction = await transaction.create_transaction(session)
    await UserModel.change_balance(session, user_id, new_balance)

    return web.json_response(dumps=lambda obj: json.dumps(obj, cls=DatetimeJsonEncoder),
                             data=new_transaction, status=200)


async def get_transaction(request: Request) -> Response:
    session: AsyncSession = request["session"]
    transaction_id = request.match_info.get('id')

    # Get transaction from the database.
    # If transaction is None then TransactionNotFound exception will be raised.
    transaction = await TransactionModel.get_transaction(session, transaction_id)

    return web.json_response(dumps=lambda obj: json.dumps(obj, cls=DatetimeJsonEncoder),
                             data=transaction, status=200)
