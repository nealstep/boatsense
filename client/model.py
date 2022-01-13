from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from .db import Base


class Name(Base):
    __tablename__ = "names"

    name = Column(String(32), primary_key=True)
    sensor = Column(Boolean, nullable=False)


class When(Base):
    __tablename__ = "whens"

    name = Column(String(32), primary_key=True, ForeignKey("names.name"))
    asat = Column(DateTime, nullable=False)
    # foreign key name


class Sensor(Base):
    __tablename__ = "sensors"

    asat = Column(DateTime, primary_key=True)
    name = Column(String(32), primary_key=True, ForeignKey("names.name"))
    data = Column(JSON, nullable=False)
