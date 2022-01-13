from logging import getLogger
from math import fabs

from boatsense import CFG, schema

LG = getLogger("{}.{}".format(CFG.name, __name__))

class Data(object):

    def __init__(self, name='data'):
        self.name = name
        self.cur = {}
        self.last = {}
        self.items = CFG.sensors[self.name].items
        self.funcs = CFG.sensors[self.name].funcs
        self.diffs = CFG.sensors[self.name].diffs

    def get(self):
        """get readings from device"""
        raise Exception("Virtual Function")

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

    def check(self):
        """check if data has changed"""
        ret = False
        if self.last:
            if self.changed():
                ret = True
        else:
            ret = True
                        

class BME280(Data):

    def __init__(self):
        super().__init__('bme280')

    def get(self) -> schema.BME280:
        # schema.BME280.schema()['properties'].keys()
        values = {
            'temperature': 21.5,
            'pressure': 999.5,
            'humidity': 20,
            'pressure_05': 0.4
        }
        data = schema.BME280(**values)
        return data


class LSM9DS1(Data):

    def __init__(self):
        super().__init__('lsm9ds1')

    def get(self) -> schema.LSM9DS1:
        values = {
            'acceleration_x': 0.1,
            'acceleration_y': 0.2,
            'acceleration_z': 8.0,
            'magnetic_x': .3,
            'magnetic_y': .4,
            'magnetic_z': .5,
            'gyro_x': 0.3,
            'gyro_y': 0.4,
            'gyro_z': 0.5,
            'temperature': 22.0
        }
        data = schema.LSM9DS1(**values)
        return data


class GPS(Data):

    def __init__(self):
        super().__init__('gps')

    def get(self) -> schema.GPS:
        values = {
            'mode': 3,
            'sats_valid': 7,
            'lat': 43.3,
            'lon': 79.2,
            'altitude': 381.2,
            'm_speed': 0.1,
            'm_track': 180.0,
            'm_climb': 0.2
        }
        data = schema.GPS(**values)
        return data