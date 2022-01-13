from adafruit_bme280.basic import Adafruit_BME280_I2C
from adafruit_lsm9ds1 import LSM9DS1_I2C
from board import I2C
from collections import deque
from copy import deepcopy
from gpsd import connect as gps_connect, get_current as gps_get_current
from gpsd import device as gps_device
from logging import getLogger
from math import fabs, log

from boatsense import CFG, schema

LG = getLogger("{}.{}".format(CFG.name, __name__))

class Data(object):

    def __init__(self, name='data'):
        self.name = name
        self.dev = None
        self.cur = {}
        self.last = {}
        self.cfg = CFG.sensors[self.name]
        self.items = self.cfg.items
        self.funcs = self.cfg.funcs
        self.diffs = self.cfg.diffs

    def get_vars(self):
        """Read device variables and call device functions to get data"""
        for i in self.items:
            self.cur[i] = getattr(self.dev, i)
        for f in self.funcs:
            self.cur[f] = getattr(self.dev, f)()

    def get(self):
        """get readings from device"""
        raise Exception("Virtual Function")

    def diff(self, item: str) -> float:
        """compute abs diff between current and last"""
        return fabs(self.cur[item] - self.last[item])

    def changed(self) -> bool:
        """check if data has changed"""
        ret = False
        for d in self.diffs:
            dv = self.diff(d)
            if dv >= self.diffs[d]:
                LG.debug("diff ({}): {} [{}]".format(d, dv, self.cur[d]))
                ret = True
        return ret

    def check(self, schemata: schema.Data) -> schema.Data:
        """check if data has changed"""
        if not self.last or self.changed():
            self.last = deepcopy(self.cur)
            items = schemata.schema()['properties'].keys()
            values = {k:v for k,v in self.cur.items() if k in items}
            data = schemata(**values)
        else:
            data = None
        return data
                        

class BME280(Data):

    def __init__(self, i2c: I2C):
        super().__init__('bme280')
        self.dev = Adafruit_BME280_I2C(i2c)
        self.press = deque(15 * [-1], 15)

    def get(self) -> schema.BME280:
        self.get_vars()
        # calculate dew point
        gamma = (self.cfg.b * self.cur['temperature'] / (self.cfg.c + self.cur['temperature'])) + log(self.cur['humidity'] / 100.0)
        self.cur['dew_point'] = (self.cfg.c * gamma) / (self.cfg.b - gamma)
        # calculate pressure change over time
        for i in (4, 9, 14):
            item = 'pressure_{:02d}'.format(i+1)
            if self.press[i] == -1:
                self.cur[item] = -1
            else:
                self.cur[item] = self.press[i] - self.cur['pressure']
        self.press.appendleft(self.cur['pressure'])
        # return data if changed
        return self.check(schema.BME280)


class LSM9DS1(Data):

    def __init__(self, i2c: I2C):
        super().__init__('lsm9ds1')
        self.dev = LSM9DS1_I2C(i2c)
        # expand tuples for diffs
        for t in self.cfg.tuples:
            for a in range(3):
                item = '{}_{}'.format(t, self.cfg.axis[a])
                if item not in self.diffs:
                    self.diffs[item] = self.diffs[t]
            del self.diffs[t]

    def get(self) -> schema.LSM9DS1:
        self.get_vars()
        # expand tuples
        for i in self.items:
            if i in self.cfg.tuples:
                self.cur[i] = list(self.cur[i])
                for j, a in enumerate(self.cfg.axis):
                    item = '{}_{}'.format(i, a)
                    self.cur[item] = self.cur[i][j]
        return self.check(schema.LSM9DS1)

class GPS(Data):

    def __init__(self):
        super().__init__('gps')
        gps_connect()
        
    def set_vars(self, level: str):
        self.items = self.cfg.items[level]
        self.funcs = self.cfg.funcs[level]
        
    def get(self) -> schema.GPS:
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
            for m in self.cfg.moves:
                m_name = "m_{}".format(m)
                self.cur[m_name] = self.cur['movement'][m]
        return self.check(schema.GPS)
