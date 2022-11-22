from datetime import date
from typing import List
from app.models.champion import Champion
from app.models.rank import Rank
from pydantic import BaseModel


class MatchBase(BaseModel):

    id = str
    queue_mode = str
    game_duration = int
    created_at = date
    status = bool


class MatchCreate(MatchBase):
    pass


class MatchUpdate(MatchBase):
    pass


class Match(MatchBase):
    class Config:
        orm_mode = True
