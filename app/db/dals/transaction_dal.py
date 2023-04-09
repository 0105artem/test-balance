from datetime import datetime
from decimal import Decimal
from typing import Union

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models import Transaction


class TransactionDAL:
    @staticmethod
    async def create_transaction(session: AsyncSession, transaction: dict) -> Union[dict, None]:
        new_transaction = Transaction(**transaction)
        session.add(new_transaction)
        try:
            await session.flush()
            await session.refresh(new_transaction)
            return new_transaction.__dict__
        except IntegrityError:
            await session.rollback()

    @staticmethod
    async def get_transaction(session: AsyncSession, uid: str) -> Union[dict, None]:
        q = await session.execute(select(Transaction).filter(Transaction.uid == uid))
        transaction = q.scalars().first()
        return transaction.__dict__ if transaction else None

    @staticmethod
    async def get_nearest_transaction(session: AsyncSession, user_id: int, search_date: datetime) -> Decimal:
        query = (
            select(Transaction.new_balance).
            filter((Transaction.user_id == user_id) & (Transaction.timestamp <= search_date)).
            order_by(Transaction.timestamp.desc())
        )
        result = await session.execute(query)
        balance = result.scalars().first()
        return balance
