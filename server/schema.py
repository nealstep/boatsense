from pydantic import BaseModel
from datetime import datetime

class Update(BaseModel):

    name: str
    asat: datetime 

    class Config:
        orm_mode = True

class Read(BaseModel):

    name: str
    asat: datetime 

    class Config:
        orm_mode = True
