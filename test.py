#!/usr/bin/env python3

from datetime import datetime, timezone
from sqlalchemy.exc import NoResultFound

from boatsense import CFG

# client overrides
CFG.db_limit = 10
CFG.db_url = "sqlite:////tmp/test.db"

from boatsense import crud, model, schema
from boatsense.db import SessionLocal, engine

model.Base.metadata.create_all(bind=engine)  
db = SessionLocal()

ddata = {
    'temperature': 21.5,
    'pressure': 999.5,
    'humidity': 20,
    'pressure_05': 0.4,
}
print(ddata)
data = schema.BME280(**ddata)
crud.add_sensor(db, "bme280", datetime.now(tz=timezone.utc), data)
crud.add_special(db, "heartbeat")
try:
    crud.add_special(db, "gps")
except NoResultFound:
    print("not Found")
sensor = crud.get_sensor(db, "bme280")
print(sensor.name)
print(sensor.asat)
print(sensor.data)

db.close()
print("Done")