import datetime
from decimal import Decimal
from typing import Optional, Union

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dals.transaction_dal import TransactionDAL
from app.db.dals.user_dals import UserDAL
from app.middlewares import exceptions
from app.schemas.user_schemas import UserBase, UserDB, UserId, UserDate


class UserModel(UserBase):
    """This class represents all methods for interacting with any user from API."""
    id: Optional[int] = None

    async def create_user(self, session: AsyncSession) -> Union[dict, None]:
        """
        Method for creating a new user in the database.

        :param session: SQLAlchemy async local session object.
        :return: dictionary with created user DB fields and values.
        :raise: UserAlreadyExists, if a user with the same name already exists in the database.
        """
        new_user = await UserDAL.create_user(session, self)

        if new_user is None:
            raise exceptions.UserAlreadyExists(self.name)

        return UserDB(**new_user).dict()

    @staticmethod
    async def change_balance(session: AsyncSession, user_id: int, new_balance: float) -> None:
        """
        Method for updating user balance in the database.

        :param session: SQLAlchemy async local session object
        :param user_id: ID of the user whose balance needs to be changed.
        :param new_balance: New balance that will be assigned to the user.
        :return: None.
        """
        await UserDAL.change_balance(session, user_id, new_balance)

    @staticmethod
    async def get_balance(session: AsyncSession, user_id: int, block: bool = False,
                          date: datetime = None) -> Union[Decimal, None]:
        """
        Method for getting user balance from the database.

        :param session: SQLAlchemy async local session object.
        :param user_id: ID of the user whose balance needs to be retrieved.
        :param block: Flag for blocking user in the database for reading and writing.
        :param date: If date is passed then balance for certain date will be returned.
        :return: User balance.
        :raises: BalanceNotFound, if user balance on the specified date is not found in the database.
        :raises: UserNotFound, if user not found in the database.
        """
        if date:
            # Date validation
            date = UserDate(date=date).date

            balance = await TransactionDAL.get_nearest_transaction(session, user_id, date)
            if balance is None:
                raise exceptions.BalanceNotFound(date)
        else:
            balance = await UserDAL.get_balance(session, user_id, block)
            if balance is None:
                raise exceptions.UserNotFound

        return balance

    @staticmethod
    async def get_user(session: AsyncSession, user_id: int) -> Union[dict, None]:
        """
        Method for getting user from the database.

        :param session: SQLAlchemy async local session object.
        :param user_id: Id of the user whose information needs to be retrieved.
        :return: Dictionary with the user fields and values from DB.
        :raises: UserNotFound, if user not found in the database.
        """
        user_id = UserId(id=user_id).id

        user = await UserDAL.get_user(session, user_id)
        if user is None:
            raise exceptions.UserNotFound(user_id)
        else:
            return UserDB(**user).dict()

    @staticmethod
    async def check_user_exists(session: AsyncSession, user_id: int) -> None:
        """
        Method for checking user existence in the database.

        :param session: SQLAlchemy async local session object.
        :param user_id: Id of the user whose existence needs to be checked.
        :return: None.
        :raises: UserNotFound, if user not found in the database.
        """
        # User id validation
        user_id = UserId(id=user_id).id

        exists = await UserDAL.check_user_exists(session, user_id)
        if not exists:
            raise exceptions.UserNotFound(user_id)
