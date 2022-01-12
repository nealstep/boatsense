from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .db import Base

class Update(Base):
    __tablename__ = "updates"

    name = Column(String(32), primary_key=True)
    asat = Column(DateTime, nullable=False)

class Read(Base):
    __tablename__ = "reads"

    name = Column(String(32), primary_key=True)
    asat = Column(DateTime, nullable=False)


