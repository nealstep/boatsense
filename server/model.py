from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .db import Base

class Dates(object):

    name = Column(String(32), primary_key=True)
    asat = Column(DateTime, nullable=False)

class Update(Dates, Base):
    __tablename__ = "updates"

class Read(Dates, Base):
    __tablename__ = "reads"

class BME280(Base):
    __tablename__ = "bme280"

    asat = Column(DateTime, primary_key=True)
    temperature = Column(Float, nullable=False)
    pressure = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    pressure_05 = Column(Float, nullable=False)
    pressure_10 = Column(Float, nullable=False)
    pressure_15 = Column(Float, nullable=False)