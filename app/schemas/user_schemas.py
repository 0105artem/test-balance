from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    name: str = Field(..., min_length=1)


class UserId(BaseModel):
    id: int = Field(0, gt=0)


class UserDate(BaseModel):
    date: datetime


class UserDB(UserBase):
    id: int
    balance: str
    created_at: datetime

    class Config:
        orm_mode = True
