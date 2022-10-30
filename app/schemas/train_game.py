from pydantic import BaseModel


class TrainGameBase(BaseModel):
    matchId: str
    status: bool


class TrainGameCreate(TrainGameBase):
    pass


class TrainGameUpdate(TrainGameBase):
    pass


class TrainGame(TrainGameBase):
    id: int

    class Config:
        orm_mode = True
