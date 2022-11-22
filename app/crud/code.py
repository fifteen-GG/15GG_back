from datetime import datetime

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
        db_obj = Code(value=code, match_id=None,
                      created_at=datetime.now())
        try:
            db.add(db_obj)
            db.commit()
        except:
            db.rollback()
        return db_obj

    def validate_code(self, db: Session, value: str):
        obj = db.query(self.model).filter_by(value=value).all()
        return obj

    def code_update(self, db: Session, code: str, match_id: str):
        try:
            db.query(self.model).filter(self.model.value == code).update(
                {'match_id': match_id}, synchronize_session=False)
            db.commit()
        except Exception as e:
            db.rollback()


code = CRUDCode(Code)
