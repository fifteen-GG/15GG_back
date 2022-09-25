from pydantic import BaseModel


class CodeBase(BaseModel):
    value: int
    created_at: str


class CodeCreate(CodeBase):
    value: int
    created_at: str


class CodeUpdate(CodeBase):
    pass


class Code(CodeBase):
    class Config:
        orm_mode = True
