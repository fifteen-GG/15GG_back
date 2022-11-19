from typing import List
from app.models.champion import Champion
from app.models.rank import Rank
from pydantic import BaseModel


class ParticipantBase(BaseModel):

    id = str
    match_id = str
    summoner_name = str
    champion_name = str
    team_id = int
    rank = str
    tier = str
    champion_level = int
    cs = int
    spell1 = str
    spell2 = str
    perk = str
    perk_style = str
    item0 = int
    item1 = int
    item2 = int
    item3 = int
    item4 = int
    item5 = int
    item6 = int
    gold_earned = int
    kills = int
    deaths = int
    assists = int
    total_damage_dealt_to_champions = int
    total_damage_taken = int
    vision_wards_bought_in_game = int
    win = bool


class ParticipantCreate(ParticipantBase):
    pass


class ParticipantUpdate(ParticipantBase):
    pass


class Summoner(ParticipantBase):
    class Config:
        orm_mode = True
