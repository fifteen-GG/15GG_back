from pydantic import BaseModel


class GameBase(BaseModel):
    data: str


class GameCreate(GameBase):
    pass


class GameUpdate(GameBase):
    pass


class Game(GameBase):
    id: int

    class Config:
        orm_mode = True
