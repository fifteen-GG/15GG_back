from sqlalchemy import Column, Integer, String

from app.database.base_class import Base


class Game(Base):
    __tablename__ = 'game'

    id = Column(Integer, primary_key=True, unique=True, index=True)
    data = Column(String, nullable=True)
