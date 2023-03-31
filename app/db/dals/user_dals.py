from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import User
from app.schemas import user_schemas


class UserDAL:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create_user(self, user: user_schemas.UserBase):
        new_user = User(**user.dict())
        self.db_session.add(new_user)
        try:
            await self.db_session.commit()
            await self.db_session.refresh(new_user)
            return new_user
        except IntegrityError as ex:
            await self.db_session.rollback()

    async def get_user(self, user_id: int):
        q = await self.db_session.execute(select(User).filter(User.id == user_id))
        return q.scalars().first()

    async def get_balance(self, user_id: int):
        q = await self.db_session.execute(select(User.balance).filter(User.id == user_id))
        return q.scalars().first()

    async def change_balance(self, user_id: int, balance: float):
        stmt = select(User).filter(User.id == user_id).with_for_update()
        q = await self.db_session.execute(stmt)
        user = q.scalars().first()
        if user:
            user.balance = balance
            await self.db_session.commit()
            await self.db_session.refresh(user)
            return user
