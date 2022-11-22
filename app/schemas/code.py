from datetime import datetime
from pydantic import BaseModel


class CodeBase(BaseModel):
    value: str
    created_at: datetime
    match_id: str | None


class CodeCreate(CodeBase):
    pass


class CodeUpdate(CodeBase):
    pass


class Code(CodeBase):
    class Config:
        orm_mode = True
