from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, TIMESTAMP
from sqlalchemy.orm import relationship
from app.database.base_class import Base


class Match(Base):
    __tablename__ = 'match'

    id = Column(String, primary_key=True, unique=True)
    queue_mode = Column(String)
    game_duration = Column(Integer)
    created_at = Column(DateTime)

    participant = relationship("Participant", back_populates="match")
