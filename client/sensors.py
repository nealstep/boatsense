#!/usr/bin/env python3
#

from adafruit_bme280.basic import Adafruit_BME280_I2C
from adafruit_lsm9ds1 import LSM9DS1_I2C
from collections import deque
from datetime import datetime, timezone
from gpsd import connect as gps_connect, get_current as gps_get_current
from gpsd import device as gps_device
from logging import getLogger
from math import log, fabs

from cfg import CFG
    
LG = getLogger("{}.{}".format(CFG.name, __name__))

class Data(object):

    _NAME = 'data'
    
    def create_table(self, table):
        """do table creates"""
        c = self.db.cursor()
        c.execute(table)
        self.db.commit()
        
    def __init__(self, db):
        LG.info("initing {}".format(self._NAME))
        self.db = db
        self.dev = None
        self.cur = {}
        self.last = {}
        self.items = CFG.sensors[self._NAME].items
        self.funcs = CFG.sensors[self._NAME].funcs
        self.diffs = CFG.sensors[self._NAME].diffs
        self.create_table(CFG.sensors['data'].table_1)
        self.create_table(CFG.sensors['data'].table_2)

    def get_vars(self):
        """read device variables and call device functions to get data"""
        self.cur['asat'] = datetime.now(timezone.utc)
        self.cur['asat_real'] = self.cur['asat'].timestamp()
        for i in self.items:
            self.cur[i] = getattr(self.dev, i)
        for f in self.funcs:
            self.cur[f] = getattr(self.dev, f)()

    def get(self):
        """get data"""
        raise Exception("Virtual Not Implemented")
            
    def diff(self, item):
        """compute abs diff between current and last"""
        return fabs(self.cur[item] - self.last[item])

    def changed(self):
        """check if data has changed"""
        ret = False
        for d in self.diffs:
            dv = self.diff(d)
            if dv >= self.diffs[d]:
                LG.debug("diff ({}): {} [{}]".format(d, dv, self.cur[d]))
                ret = True
        return ret
    
    def insert(self, query, data, commit=True):
        """do table inserts"""
        c = self.db.cursor()
        c.execute(query, data)
        if commit:
            self.db.commit()
            
    def save(self):
        """save data and update last update"""
        self.insert(CFG.sensors['data'].insert,
                        (self._NAME, self.cur['asat_real']), False)
        if CFG.sensors[self._NAME].saves:
            self.last = self.cur.copy()
            data = [self.cur[i] for i in CFG.sensors[self._NAME].saves]
            LG.debug("{}; {}".format(self._NAME, data))
            self.insert(CFG.sensors[self._NAME].insert, data)
        
    def check(self):
        """check if data has changed"""
        if self.last:
            if self.changed():
                self.save()
        else:
            self.save()
                        
    
class BME280(Data):

    _NAME = 'bme280'
    
    def __init__(self, db, i2c):
        super().__init__(db)
        self.dev = Adafruit_BME280_I2C(i2c)
        self.press = deque(15 * [-1], 15)
        self.create_table(CFG.sensors[self._NAME].table)
        self.b = CFG.sensors[self._NAME].b
        self.c = CFG.sensors[self._NAME].c
        
    def get(self):
        self.get_vars()
        gamma = (self.b * self.cur['temperature'] \
                     / (self.c + self.cur['temperature'])) \
                     + log(self.cur['humidity'] / 100.0)
        self.cur['dew_point'] = (self.c * gamma) / (self.b - gamma)
        for i in (4, 9, 14):
            item = 'pressure_{:02d}'.format(i+1)
            if self.press[i] == -1:
                self.cur[item] = -1
            else:
                self.cur[item] = self.press[i] - self.cur['pressure']
        self.press.appendleft(self.cur['pressure'])
        self.check()

        
class LSM9DS1(Data):

    _NAME = 'lsm9ds1'

    def __init__(self, db, i2c):
        super().__init__(db)
        self.dev = LSM9DS1_I2C(i2c)
        self.tuples = CFG.sensors[self._NAME].tuples
        self.axis = CFG.sensors[self._NAME].axis
        for t in self.tuples:
            for a in range(3):
                item = '{}_{}'.format(t, self.axis[a])
                if item not in self.diffs:
                    self.diffs[item] = self.diffs[t]
            del self.diffs[t]
        self.create_table(CFG.sensors[self._NAME].table)

    def get(self):
        self.get_vars()
        for i in self.items:
            if i in self.tuples:
                self.cur[i] = list(self.cur[i])
                for a in range(3):
                    item = '{}_{}'.format(i, self.axis[a])
                    self.cur[item] = self.cur[i][a]
        self.check()

        
class GPS(Data):

    _NAME = 'gps'
    
    def __init__(self, db):
        super().__init__(db)
        gps_connect()
        self.create_table(CFG.sensors[self._NAME].table)        
        
    def set_vars(self, level):
        self.items = CFG.sensors[self._NAME].items[level]
        self.funcs = CFG.sensors[self._NAME].funcs[level]
        
    def get(self):
        self.dev = gps_get_current()
        self.cur['device'] = gps_device()
        self.set_vars('0')
        self.get_vars()
        if self.cur['mode'] >= 2:
            self.set_vars('2')
            self.get_vars()
            self.cur['time_utc'] = self.dev.get_time()
            self.cur['time_local'] = self.dev.get_time(True)
        if self.cur['mode'] >= 3:
            self.set_vars('3')
            self.get_vars()
            for m in CFG.sensors[self._NAME].moves:
                m_name = "m_{}".format(m)
                self.cur[m_name] = self.cur['movement'][m]
        self.check()
