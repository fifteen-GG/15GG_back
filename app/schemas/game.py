from pydantic import BaseModel


class CodeBase(BaseModel):
    id: int
    data: str | None


class CodeCreate(CodeBase):
    pass


class Code(CodeBase):

    class Config:
        orm_mode = True
