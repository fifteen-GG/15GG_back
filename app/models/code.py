from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database.base_class import Base


class Code(Base):
    __tablename__ = 'code'

    value = Column(String, primary_key=True, unique=True,
                   index=True)
    match_id = Column(String, ForeignKey("match.id"), nullable=True)
    created_at = Column(DateTime)

    match = relationship("Match", back_populates="code")
