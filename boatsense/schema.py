from datetime import datetime
from pydantic import BaseModel
from pydantic.types import Json
from typing import Optional


class RObject(BaseModel):
    '''base for all returned data'''
    pass

class Data(RObject):
    '''Base for all sensor data'''
    pass

class BME280(Data):
    '''BME280 Data'''
    temperature: float
    pressure: float
    humidity: float
    pressure_05: Optional[float]
    pressure_10: Optional[float]
    pressure_15: Optional[float]

class LSM9DS1(Data):
    '''LSM9DS1 Data'''
    acceleration_x: float
    acceleration_y: float
    acceleration_z: float
    magnetic_x: float
    magnetic_y: float
    magnetic_z: float
    gyro_x: float
    gyro_y: float
    gyro_z: float
    temperature: float

class GPS(Data):
    '''GPS Data'''
    mode: int
    sats_valid: int
    lat: Optional[float]
    lon: Optional[float]
    altitude: Optional[float]
    m_speed: Optional[float]
    m_track: Optional[float]
    m_climb:Optional[float]
    lat_map: Optional[str]
    lon_map: Optional[str]

class DateInfo(RObject):
    '''date info'''
    name: str
    sensor: bool
    asat: Optional[datetime]

class Message(RObject):
    '''simple message'''
    msg: str


class ORMModel(BaseModel):
    '''Base for all ORM based models'''
    class Config:
        orm_mode = True

class Item(ORMModel):
    '''Name model'''
    name: str
    sensor: bool
    asat: datetime

class Sensor(ORMModel):
    '''sensor data model'''
    name: str
    asat: datetime
    data: Data
