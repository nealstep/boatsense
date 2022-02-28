#!/usr/bin/env python3

from board import I2C
from datetime import datetime, timezone
from json import dumps
from logging import getLogger
from paho.mqtt import client as mqtt
from schedule import every, run_pending
from sqlalchemy.orm import Session
from time import sleep

from boatsense import CFG
from boatsense import crud, model, schema, sensors
from boatsense.db import SessionLocal, engine

LG = getLogger("{}.{}".format(CFG.name, 'client'))


class Client(object):

    def __init__(self, db: Session):
        self.db = db
        i2c = I2C()
        self.sensors = {}
        self.sensors['bme280'] = sensors.BME280(i2c)
        self.sensors['lsm9ds1'] = sensors.LSM9DS1(i2c)
        self.sensors['gps'] = sensors.GPS()
        self.mqtt = mqtt.Client("VivaceS1")
        self.mqtt.connect(CFG.mqtt)
        for t in CFG.timings:
            every(CFG.timings[t]).seconds.do(self.get_reading, name=t)
        self.sleep = min(CFG.timings.values())

    def display(self, name: str, data: schema.Data):
        out = {}
        for i in range(7):
            nm = "line_{}".format(i)
            out[nm] = CFG.out[0][name][i].format(**(data.dict()))
        LG.debug(out)
        self.mqtt.publish(CFG.mqtt_topic.format(name), dumps(out), retain=True)

    def upload(self):
        LG.warning("Not Implemented: upload")

    def get_reading(self, name: str):
        #self.mqtt.publish(CFG.mqtt_topic.format("log"), "reading")
        if name in self.sensors:
            data = self.sensors[name].get()
            if data:
                asat = datetime.now(tz=timezone.utc)
                crud.add_sensor(self.db, name, asat, data)
                self.display(name, data)
        else:
            if name == 'upload':
                self.upload()
            elif name == 'heartbeat':
                LG.debug("{}: {}".format(CFG.mqtt_topic.format(name), "{x:H}"))
                self.mqtt.publish(CFG.mqtt_topic.format(name), "{x:H}")
                crud.add_special(self.db, name) # once upload is implemented should be unindented

    def run(self):
        LG.info("Running")
        self.mqtt.loop_start()
        self.mqtt.publish(CFG.mqtt_topic.format("heartbeat"), "{x:B}")
        try:
            while True:
                run_pending()
                sleep(self.sleep)
        finally:
            self.mqtt.publish(CFG.mqtt_topic.format("heartbeat"), "{x:E}")
            self.mqtt.loop_stop()

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
