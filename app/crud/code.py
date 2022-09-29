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
        code = generate_code()
        if len(db.query(self.model).filter_by(value=code).all()) > 0:
            code = generate_code()
        db_obj = self.model(value=code, created_at=datetime.now())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def validate_code(self, db: Session, value: str):
        obj = db.query(self.model).filter_by(value=value).all()
        return obj


code = CRUDCode(Code)
