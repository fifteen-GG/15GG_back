from pydantic import BaseModel


class RankBase(BaseModel):
    tier: str
    rank: str
    lp: int
    wins: int
    losses: int
    is_flex: bool


class RankCreate(RankBase):
    pass


class RankUpdate(RankBase):
    pass


class Rank(RankBase):
    id: int
    summoner_id: str

    class Config:
        orm_mode = True
