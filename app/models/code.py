from enum import unique
from operator import index
from sqlalchemy import Column, Integer, String, DateTime

from database import Base


class Code(Base):
    __tablename__ = 'code'

    value = Column(Integer, primary_key=True, unique=True, index=True)
    created_at = Column(DateTime)