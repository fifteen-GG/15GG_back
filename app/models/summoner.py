from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from app.database.base_class import Base


class Summoner(Base):
    __tablename__ = 'summoner'

    id = Column(String, primary_key=True, unique=True)
    puuid = Column(String, unique=True)
    name = Column(String, unique=True)
    level = Column(Integer)
    profile_icon_id = Column(String)
    kda_avg = Column(Float)
    kills_avg = Column(Float)
    deaths_avg = Column(Float)
    assists_avg = Column(Float)
    prefer_position = Column(String)
    prefer_position_rate = Column(Float)

    rank = relationship("Rank", back_populates="summoner")
    champion = relationship("Champion", back_populates="summoner")
