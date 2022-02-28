from datetime import datetime, timezone
from sqlalchemy.orm import Session

from boatsense import CFG, model, schema

def add_special(db: Session, name: str) -> None:
    '''Add a special entry (one without a sensor)'''
    item = db.query(model.Item).filter(model.Item.name==name,model.Item.sensor==False).one()
    item.asat = datetime.now(tz=timezone.utc)
    db.commit()

def add_sensor(db: Session, name: str, asat: datetime, data: schema.Data) -> None:
    '''Add sensor data updating names with last update time'''
    sensor = model.Sensor(name=name, asat=asat, data=data.json())
    db.merge(sensor)
    item = db.query(model.Item).filter(model.Item.name==name, model.Item.sensor==True).one()
    item.asat = asat
    db.commit()

def _convert_to_dict(o: schema.ORMModel) -> schema.Message:
    d = {c.name: getattr(o, c.name) for c in o.__table__.columns}
    return d

def _convert_to_array(a: list[schema.ORMModel]) -> list[schema.Message]:
    l = [ _convert_to_dict(i) for i in a]
    return l

def get_sensor(db: Session, name: str) -> schema.Data:
    '''Get latest sensor reading'''
    item = db.query(model.Item).filter(model.Item.name==name, model.Item.sensor==True).one()
    sensor = db.query(model.Sensor).filter(model.Sensor.name==name,model.Sensor.asat==item.asat).one()
    return _convert_to_dict(sensor)

def get_date(db: Session, name: str) -> schema.DateInfo:
    '''get dates'''
    item = db.query(model.Item).filter(model.Item.name==name).one()
    return _convert_to_dict(item)

def get_dates(db: Session, skip: int=0, limit: int=CFG.db_limit) -> list[schema.DateInfo]:
    '''get dates'''
    items = db.query(model.Item).offset(skip).limit(limit).all()
    return _convert_to_array(items)
