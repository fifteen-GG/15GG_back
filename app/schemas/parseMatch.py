from pydantic import BaseModel


class ParseMatchBase(BaseModel):
    matchId: str
    status: bool


class ParseMatchCreate(ParseMatchBase):
    pass


class ParseMatchUpdate(ParseMatchBase):
    pass


class ParseMatch(ParseMatchBase):
    id: int

    class Config:
        orm_mode = True
