from typing import List
from app.models.champion import Champion
from app.models.rank import Rank
from pydantic import BaseModel


class SummonerBase(BaseModel):
    id: str
    puuid: str
    name: str
    level: int
    profile_icon_id: str
    kda_avg: float
    kills_avg: float
    deaths_avg: float
    assists_avg: float
    prefer_position: str
    prefer_position_rate: float


class SummonerCreate(SummonerBase):
    pass


class SummonerUpdate(SummonerBase):
    pass


class Summoner(SummonerBase):
    rank: List[Rank] = []
    champion: List[Champion] = []

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
