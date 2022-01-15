#!/usr/bin/env python3

from board import I2C
from datetime import datetime, timezone
from logging import getLogger
from paho.mqtt import client as mqtt
from schedule import every, run_pending
from socket import AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR, SO_BROADCAST
from socket import socket
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
        self.network()
        self.sensors = {}
        self.sensors['bme280'] = sensors.BME280(i2c)
        self.sensors['lsm9ds1'] = sensors.LSM9DS1(i2c)
        self.sensors['gps'] = sensors.GPS()
        for t in CFG.timings:
            every(CFG.timings[t]).seconds.do(self.get_reading, name=t)
        self.sleep = min(CFG.timings.values())

    def network(self):
        self.server = socket(AF_INET, SOCK_DGRAM)
        self.server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.mqtt = mqtt.Client("S1")
        self.mqtt.connect(CFG.mqtt)

    def upload(self):
        LG.warning("Not Implemented: upload")

    def get_reading(self, name: str):
        if name in self.sensors:
            data = self.sensors[name].get()
            if data:
                LG.debug("New data: {}".format(name))
                asat = datetime.now(tz=timezone.utc)
                crud.add_sensor(self.db, name, asat, data)
                LG.debug("{}: {}".format(CFG.mqtt_topic.format(name), data.json()))
                self.mqtt.publish(CFG.mqtt_topic.format(name), data.json())
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
