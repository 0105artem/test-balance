from decimal import Decimal
from typing import Union

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.schemas import user_schemas


class UserDAL:
    @staticmethod
    async def create_user(session: AsyncSession, user: user_schemas.UserBase) -> Union[dict, None]:
        new_user = User(**user.dict())
        session.add(new_user)
        try:
            await session.flush()
            await session.refresh(new_user)
            return new_user.__dict__
        except IntegrityError as ex:
            await session.rollback()

    @staticmethod
    async def get_user(session: AsyncSession, user_id: int) -> Union[dict, None]:
        q = await session.execute(select(User).filter(User.id == user_id))
        user = q.scalars().first()
        return user.__dict__ if user else None

    @staticmethod
    async def get_balance(session: AsyncSession, user_id: int, block: bool = False) -> Union[Decimal, None]:
        stmt = select(User.balance).filter(User.id == user_id)
        if block:
            stmt = stmt.with_for_update()
        q = await session.execute(stmt)
        return q.scalars().first()

    @staticmethod
    async def check_user_exists(session: AsyncSession, user_id: int) -> bool:
        stmt = select(User.id).filter(User.id == user_id)
        q = await session.execute(stmt)
        user = q.scalars().first()
        return user is not None

    @staticmethod
    async def change_balance(session: AsyncSession, user_id: int, balance: float):
        stmt = select(User).filter(User.id == user_id)
        q = await session.execute(stmt)
        user = q.scalars().first()
        if user:
            user.balance = balance
            await session.flush()
            await session.refresh(user)
            return user
