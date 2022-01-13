#!/usr/bin/env python3

from datetime import datetime, timezone
from logging import getLogger
from schedule import every, run_pending
from sqlalchemy.orm import Session
from time import sleep

from boatsense import CFG

# client overrides
CFG.db_limit = 10
CFG.db_url = "sqlite:////tmp/test.db"
# logger
LG = getLogger("{}.{}".format(CFG.name, 'client'))

from boatsense import crud, model, schema, sensors
from boatsense.db import SessionLocal, engine


class Client(object):

    def __init__(self, db: Session):
        self.db = db
        self.sensors = {}
        self.sensors['bme280'] = sensors.BME280()
        self.sensors['lsm9ds1'] = sensors.LSM9DS1()
        self.sensors['gps'] = sensors.GPS()
        for t in CFG.timings:
            every(CFG.timings[t]).seconds.do(self.get_reading, name=t)
        self.sleep = min(CFG.timings.values())

    def get_reading(self, name: str):
        if name in self.sensors:
            data = self.sensors[name].get()
            asat = datetime.now(tz=timezone.utc)
            crud.add_sensor(self.db, name, asat, data)
        else:
            if name == 'upload':
                self.upload()
            crud.add_special(self.db, name)

    def run(self):
        LG.info("Running")
        while True:
            run_pending()
            sleep(self.sleep)

if __name__ == "__main__":
    LG.info("Starting Client")
    model.Base.metadata.create_all(bind=engine)  
    db = SessionLocal()
    try:
        client = Client(db)
        client.run()
    finally:
        LG.warning("Closing DB")
        db.close()