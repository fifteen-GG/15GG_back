from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from app.database.base_class import Base


class Participant(Base):
    __tablename__ = 'participant'

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    match_id = Column(String, ForeignKey("match.id"))
    summoner_name = Column(String)
    champion_name = Column(String)
    team_id = Column(Integer)
    rank = Column(String)
    tier = Column(String)
    champion_level = Column(Integer)
    cs = Column(Integer)
    spell1 = Column(String)
    spell2 = Column(String)
    perk = Column(String)
    perk_style = Column(String)
    item0 = Column(Integer)
    item1 = Column(Integer)
    item2 = Column(Integer)
    item3 = Column(Integer)
    item4 = Column(Integer)
    item5 = Column(Integer)
    item6 = Column(Integer)
    gold_earned = Column(Integer)
    kills = Column(Integer)
    deaths = Column(Integer)
    assists = Column(Integer)
    total_damage_dealt_to_champions = Column(Integer)
    total_damage_taken = Column(Integer)
    vision_wards_bought_in_game = Column(Integer)
    win = Column(Boolean)

    match = relationship("Match", back_populates="participant")
