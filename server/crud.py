from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import null

from . import DB_LIMIT, model, schema

def get_dates(db: Session, dates: model.Dates, skip: int=0, limit: int=DB_LIMIT):
    return db.query(dates).offset(skip).limit(limit).all()

def get_date(db: Session, dates: model.Dates, name: str):
    return db.query(dates).filter(dates.name == name).first()

def set_date(db: Session, dates: model.Dates, name: str, asat: datetime):
    item = dates(name=name, asat=asat)
    db.merge(item)
    db.commit()
    return item

def get_bme(db: Session):
    item = db.query(model.Update).filter(model.Update.name == 'bme280').first()
    if item:
        print(item.asat)
        data = db.query(model.BME280).filter(model.BME280.asat == item.asat).first()
    else:
        data = null
    return data

def set_bme(db: Session, asat: datetime, temperature: float, pressure: float, humidity: float, pressure_05: float, pressure_10: float, pressure_15: float):
    item = model.BME280(asat=asat, temperature=temperature, pressure=pressure, humidity=humidity, pressure_05=pressure_05, pressure_10=pressure_10, pressure_15=pressure_15)
    db.merge(item)
    db.commit()
    return item