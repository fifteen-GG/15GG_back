from enum import unique
from operator import index
from sqlalchemy import Column, Integer, String, DateTime

from database import Base


class Game(Base):
    __tablename__ = 'game'

    id = Column(Integer, primary_key=True, unique=True, index=True)
    data = Column(String, nullable=True)
