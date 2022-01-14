from datetime import datetime, timezone
from sqlalchemy.orm import Session

from boatsense import model, schema

def add_special(db: Session, name: str):
    '''Add a special entry (one without a sensor)'''
    item = db.query(model.Item).filter(model.Item.name==name,model.Item.sensor==False).one()
    item.asat = datetime.now(tz=timezone.utc)
    db.commit()

def add_sensor(db: Session, name: str, asat: datetime, data: schema.Data):
    '''Add sensor data updating names with last update time'''
    sensor = model.Sensor(name=name, asat=asat, data=data.json())
    db.merge(sensor)
    item = db.query(model.Item).filter(model.Item.name==name, model.Item.sensor==True).one()
    item.asat = asat
    db.commit()

def get_sensor(db: Session, name: str) -> schema.Data:
    '''Get latest sensor reading'''
    item = db.query(model.Item).filter(model.Item.name==name, model.Item.sensor==True).one()
    sensor = db.query(model.Sensor).filter(model.Sensor.name==name,model.Sensor.asat==item.asat).one()
    return sensor
