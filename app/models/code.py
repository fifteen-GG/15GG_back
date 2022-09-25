from sqlalchemy import Column, Integer, DateTime

from app.database.base_class import Base


class Code(Base):
    __tablename__ = 'code'

    value = Column(Integer, primary_key=True, unique=True, index=True)
    created_at = Column(DateTime)
