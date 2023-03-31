from datetime import datetime

from pydantic import BaseModel, Field


class TransactionBase(BaseModel):
    uid: str = Field(..., min_length=1)
    user_id: int
    type: str
    amount: float = Field(0.0, gt=0)
    timestamp: datetime


class TransactionDB(BaseModel):
    uid: str = Field(..., min_length=1)
    user_id: int
    type: str
    amount: str
    timestamp: datetime
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class TransactionId(BaseModel):
    uid: str = Field(..., min_length=1)
