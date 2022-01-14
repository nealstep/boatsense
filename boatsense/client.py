#!/usr/bin/env python3

from board import I2C
from datetime import datetime, timezone
from logging import getLogger
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
        self.listen = socket(AF_INET, SOCK_DGRAM)
        self.listen.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.listen.setblocking(False)
        self.listen.bind(CFG.upd_listen)
        self.send = False

    def upload(self):
        LG.warning("Not Implemented: upload")
        
    def get_reading(self, name: str):
        if name in self.sensors:
            data = self.sensors[name].get()
            if data:
                asat = datetime.now(tz=timezone.utc)
                crud.add_sensor(self.db, name, asat, data)
                if self.send:
                    LG.debug("sending udp")
                    msg = '{{"{}": {}}}'.format(name, data.json()).encode('utf-8')
                    self.server.sendto(msg, CFG.udp_addr)
        else:
            if name == 'upload':
                self.upload()
            crud.add_special(self.db, name)

    def run(self):
        LG.info("Running")
        while True:
            run_pending()
            try:
                data, addr = self.listen.recvfrom(1024)
                if data:
                    if data.decode('utf-8') == 'T':
                        LG.info("Sending UDP on")
                        self.send = True
                    else:
                        LG.info("Sending UDP off")
                        self.send = False
            except BlockingIOError:
                pass
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
