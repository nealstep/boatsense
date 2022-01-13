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
            every(CFG.timings[t]).seconds.do(getattr(self, t))
        self.sleep = min(CFG.timings.values())

    def get_reading(self, name: str):
        asat = datetime.now(tz=timezone.utc)
        data = self.sensors[name].get()
        crud.add_sensor(self.db, name, asat, data)

    def bme280(self):
        LG.debug("bme280")
        self.get_reading('bme280')

    def lsm9ds1(self):
        LG.debug("lsm9ds1")
        self.get_reading('lsm9ds1')

    def gps(self):
        LG.debug("gps")
        self.get_reading('gps')

    def heartbeat(self):
        LG.debug("Heartbeat")
        crud.add_special(self.db, 'heartbeat')

    def upload(self):
        LG.debug("Upload")
        crud.add_special(self.db, 'upload')
        LG.error("Not Implemented: upload")

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
        LG.info("Closing DB")
        db.close()