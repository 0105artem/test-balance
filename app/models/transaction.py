from decimal import Decimal
from typing import Union, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dals.transaction_dal import TransactionDAL
from app.middlewares import exceptions
from app.schemas.transaction_schemas import TransactionBase, TransactionDB, TransactionId


class TransactionModel(TransactionBase):
    new_balance: Optional[float]

    async def create_transaction(self, session: AsyncSession) -> dict:
        """
        Method for creating a new transaction in the database.

        :param session: SQLAlchemy async local session object.
        :return: Dictionary with created transaction DB fields and values.
        """
        new_transaction = await TransactionDAL.create_transaction(session, self.dict())
        new_transaction = TransactionDB(**new_transaction)
        return new_transaction.dict()

    @staticmethod
    async def get_transaction(session: AsyncSession, transaction_id: str) -> Union[dict, None]:
        """
        Method for getting transaction from the Database.

        :param session: SQLAlchemy async local session object.
        :param transaction_id: UUID of the transaction record to retrieve.
        :return: Dictionary with the transaction fields and values from DB.
        :raises TransactionNotFound: if the specified transaction ID is not found in the database
        """
        # Transaction uuid validation
        transaction_id = TransactionId(uid=transaction_id).uid

        transaction = await TransactionDAL.get_transaction(session, transaction_id)
        if transaction is not None:
            transaction = TransactionDB(**transaction)
            return transaction.dict()
        else:
            raise exceptions.TransactionNotFound(transaction_id)

    async def check_transaction_exists(self, session: AsyncSession) -> None:
        """
        Method for checking if transaction with the same UUID already exists in the database.

        :param session: SQLAlchemy async local session object.
        :return: None.
        :raises TransactionAlreadyExists: If transaction with the same UUID already exists in the database.
        """
        if await TransactionDAL.get_transaction(session, self.uid):
            raise exceptions.TransactionAlreadyExists(self.uid)

    async def calculate_balance(self, balance: Decimal) -> Union[float, None]:
        """
        Method for calculating new balance of the user after the transaction is made.

        :param balance: Balance of the user before transaction.
        :return: Balance of the user after the transaction.
        :raises InsufficientFunds: If user doesn't have enough money to withdraw.
        :raises UnknownTransactionType: If an invalid type of the transaction is specified.
        """
        if self.type == "DEPOSIT":
            new_balance = float(balance) + self.amount
        elif self.type == "WITHDRAW":
            new_balance = float(balance) - self.amount
            # Check if user has enough money to withdraw
            if new_balance < 0:
                raise exceptions.InsufficientFunds
        else:
            raise exceptions.UnknownTransactionType

        self.new_balance = new_balance
        return new_balance
