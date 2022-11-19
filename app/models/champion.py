from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base_class import Base


class Champion(Base):
    __tablename__ = 'champion'

    id = Column(Integer, primary_key=True, autoincrement=True)
    summoner_id = Column(String, ForeignKey("summoner.id"))
    champion_name = Column(String)
    counts = Column(Integer)
    kills = Column(Integer)
    deaths = Column(Integer)
    assists = Column(Integer)
    wins = Column(Integer)
    order = Column(Integer)

    summoner = relationship("Summoner", back_populates="champion")
