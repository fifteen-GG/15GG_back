from pydantic import BaseModel


class CodeBase(BaseModel):
    value: int
    created_at: str

class CodeCreate(CodeBase):
    pass


class Code(CodeBase):
    
    class Config:
        orm_mode = True
