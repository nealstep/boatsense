from pydantic import BaseModel
from datetime import datetime

class ORMModel(BaseModel):

    class Config:
        orm_mode = True

class Update(ORMModel):

    name: str
    asat: datetime 
    
class Read(ORMModel):

    name: str
    asat: datetime 

class BME280(ORMModel):

    asat: datetime
    temperature: float
    pressure: float
    humidity: float
    pressure_05: float
    pressure_10: float
    pressure_15: float