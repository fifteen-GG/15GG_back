from typing import Optional, List

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.code import Code
from app.schemas.code import CodeCreate, CodeUpdate


class CRUDCode(CRUDBase[Code, CodeCreate, CodeUpdate]):
    # Declare model specific CRUD operation methods.
    pass


code = CRUDCode(Code)
