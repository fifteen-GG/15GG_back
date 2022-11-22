from pydantic import BaseModel


class ChampionBase(BaseModel):
    champion_name: str
    counts = int
    kills = int
    deaths = int
    assists = int
    wins = int


class ChampionCreate(ChampionBase):
    pass


class ChampionUpdate(ChampionBase):
    pass


class Champion(ChampionBase):
    id: int
    summoner_id: str

    class Config:
        orm_mode = True
