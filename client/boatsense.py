#!/usr/bin/env python3
#

from board import I2C
from logging import Formatter, StreamHandler, getLogger
from logging.handlers import TimedRotatingFileHandler
from schedule import every, run_pending
from sqlite3 import connect as db_con
from time import sleep

from cfg import CFG
from sensors import Data, BME280, LSM9DS1, GPS

LG = getLogger(CFG.name)
LG.propagate = False
    
def setup_logger():
    sth = StreamHandler()
    form1 = Formatter(CFG.log_fmt, datefmt=CFG.log_fmt_dt)
    sth.setFormatter(form1)
    LG.addHandler(sth)
    fh = TimedRotatingFileHandler(CFG.log_file, when='midnight', backupCount=3)
    form2 = Formatter(CFG.log_fmt, datefmt=CFG.log_fmt_dt)
    fh.setFormatter(form2)
    LG.addHandler(fh)
    LG.setLevel(CFG.log_levels[CFG.log_lvl])


class BoatSense(object):

    def __init__(self):
        i2c = I2C()
        db = db_con(CFG.db_file)
        if not db:
            raise Exception("Unable to make DB connection")
        self.data = Data(db)
        self.bme280 = BME280(db, i2c)
        self.lsm9ds1 = LSM9DS1(db, i2c)
        self.gps = GPS(db)
        devs = {
            'bme280': self.bme280,
            'lsm9ds1': self.lsm9ds1,
            'gps': self.gps,
            }
        for dev in devs:
            every(CFG.timings[dev]).seconds.do(devs[dev].get)
        every(CFG.timings['heartbeat']).seconds.do(self.heartbeat)
        every(CFG.timings['upload']).seconds.do(self.upload)
        self.sleep = min(CFG.timings.values())

    def heartbeat(self):
        LG.info("Heartbeat")
        self.data.get_vars()
        self.data.save()

    def upload(self):
        LG.info("Upload")
        # check if new data
        # upload new data
    
    def run(self):
        LG.info("Running")
        while True:
            run_pending()
            sleep(self.sleep)
        
if __name__ == '__main__':
    setup_logger()
    LG.info("Starting")
    boat_sense = BoatSense()
    boat_sense.run()
