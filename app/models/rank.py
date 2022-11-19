from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base_class import Base


class Rank(Base):
    __tablename__ = 'rank'

    id = Column(Integer, primary_key=True, autoincrement=True)
    summoner_id = Column(String, ForeignKey("summoner.id"))
    tier = Column(String)
    rank = Column(String)
    lp = Column(Integer)
    wins = Column(Integer)
    losses = Column(Integer)
    is_flex = Column(Boolean)

    summoner = relationship("Summoner", back_populates="rank")
