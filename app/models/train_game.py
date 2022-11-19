from sqlalchemy import Column, Integer, String, Boolean

from app.database.base_class import Base


class TrainGame(Base):
    __tablename__ = 'train_game'

    id = Column(Integer, primary_key=True, unique=True, index=True)
    match_id = Column(String, unique=True, index=True)
    is_parsed = Column(Boolean, default=False)
