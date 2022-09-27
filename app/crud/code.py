from datetime import datetime
from typing import Optional, List

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.code import Code
from app.schemas.code import CodeCreate, CodeUpdate
from app.utils.code import generate_code


class CRUDCode(CRUDBase[Code, CodeCreate, CodeUpdate]):
    # Declare model specific CRUD operation methods.

    def create_code(self, db: Session):
        db_obj = self.model(value=generate_code(), created_at=datetime.now())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


code = CRUDCode(Code)
