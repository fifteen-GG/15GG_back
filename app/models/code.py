from sqlalchemy import Column, String, DateTime

from app.database.base_class import Base


class Code(Base):
    __tablename__ = 'code'

    value = Column(String, primary_key=True, unique=True, index=True)
    created_at = Column(DateTime)
