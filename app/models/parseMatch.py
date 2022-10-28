from sqlalchemy import Column, Integer, String, Boolean

from app.database.base_class import Base


class ParseMatch(Base):
    __tablename__ = 'parseMatch'

    id = Column(Integer, primary_key=True, unique=True, index=True)
    matchId = Column(String, unique=True, index=True)
    status = Column(Boolean, default=False)
