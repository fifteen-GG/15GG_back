from typing import Optional
from pydantic import BaseModel


class TrainGameBase(BaseModel):
    match_id: str
    is_parsed: bool


class TrainGameCreate(TrainGameBase):
    pass


class TrainGameUpdate(TrainGameBase):
    pass


class TrainGame(TrainGameBase):
    id: Optional[int]

    class Config:
        orm_mode = True
