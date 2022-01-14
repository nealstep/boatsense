from sqlalchemy import event, Column, String, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.engine import Connection
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Table

from boatsense import CFG
from boatsense.db import Base


class Item(Base):
    '''Names that we record data for'''
    __tablename__ = "items"

    name = Column(String(32), primary_key=True)
    sensor = Column(Boolean, nullable=False)
    asat = Column(DateTime, nullable=True)

@event.listens_for(Item.__table__, "after_create")
def insert_names(target: Table, connection: Connection, **kw):
    '''auto table populating code'''
    for item in CFG.initial_name_data:
        connection.execute(target.insert(), item)


class Sensor(Base):
    '''Sensor data readings'''
    __tablename__ = "sensors"

    name = Column(String(32), ForeignKey(Item.name), primary_key=True)
    asat = Column(DateTime, primary_key=True)
    data = Column(JSON, nullable=False)
