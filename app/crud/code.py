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
        db_obj = Code(value=code, match_id='KR_6226957014',
                      created_at=datetime.now())
        try:
            db.add(db_obj)
            db.commit()
        except:
            db.rollback()
            print("hello")
        return db_obj

    def validate_code(self, db: Session, value: str):
        obj = db.query(self.model).filter_by(value=value).all()
        return obj

    def update_code(self, db: Session, code: str, match_id: str):
        try:
            db.query(self.model).filter(self.model.value == code).update(
                {self.model.match_id: match_id}, synchronize_session=False)
        except Exception as e:
            print(e)
        res = db.query(self.model).filter(self.model.value == code).all()
        print(res[0].match_id)


code = CRUDCode(Code)
