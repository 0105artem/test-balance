from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from .config import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False, unique=True)
    balance = Column(Numeric(10, 2), nullable=False, default=0.00)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    __table_args__ = (CheckConstraint('balance >= 0', name='positive_balance'),)


class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, nullable=False)
    uid = Column(String, nullable=False, unique=True)
    type = Column(String, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    new_balance = Column(Numeric(10, 2), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    user = relationship("User")

    __table_args__ = (CheckConstraint('amount >= 0', name='positive_amount'),)
