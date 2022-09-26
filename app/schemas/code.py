from datetime import datetime
from pydantic import BaseModel


class CodeBase(BaseModel):
    value: str
    created_at: datetime


class CodeCreate(CodeBase):
    value: str
    created_at: datetime


class CodeUpdate(CodeBase):
    pass


class Code(CodeBase):
    class Config:
        orm_mode = True
