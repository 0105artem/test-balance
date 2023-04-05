from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from app.db.models import Transaction
from app.schemas import transaction_schemas


class TransactionDAL:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create_transaction(self, transaction: dict):
        new_transaction = Transaction(**transaction)
        self.db_session.add(new_transaction)
        try:
            await self.db_session.commit()
            await self.db_session.refresh(new_transaction)
            return new_transaction
        except IntegrityError:
            await self.db_session.rollback()

    async def get_transaction(self, uid: str):
        q = await self.db_session.execute(select(Transaction).filter(Transaction.uid == uid))
        return q.scalars().first()

    async def get_nearest_transaction(self, search_date: datetime):
        query = select(Transaction.new_balance).where(Transaction.timestamp < search_date).\
                      order_by(Transaction.timestamp.desc()).limit(1)
        result = await self.db_session.execute(query)
        return result.scalars().first()
