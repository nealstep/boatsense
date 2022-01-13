from datetime import datetime
from pydantic import BaseModel
from pydantic.types import Json
from typing import Optional


class Data(BaseModel):
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
    lat: float
    lon: float
    altitude: float
    m_speed: float
    m_track: float
    m_climb:float


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