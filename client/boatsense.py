#!/usr/bin/env python3
#

from adafruit_bme280.basic import Adafruit_BME280_I2C
from adafruit_lsm9ds1 import LSM9DS1_I2C
from board import I2C
from datetime import datetime
from time import time, sleep

from lcd_i2c import LCD_I2C
from pbut import PBut

_DEG = chr(223)
_SCREEN_MAX = 3
_SLEEP = 0.05
_TIME = {'off': 30, 'update': 1, 'temp': 60, 'gps': 1, 'lsm': 1}
_LATF = "Lat {latd:3d}\337{latm:8.4f}{latc:1s}"
_LONF = "Lon {lond:03d}\337{lonm:8.4f}{lonc:1s}"
_BME_B = 17.62
_BME_C = 243.12

class BoatSense:

    def __init__(self):
        i2c = I2C()
        self.pbut = PBut()
        self.lcd = LCD_I2C(i2c)
        self.lcd.display(False)
        self.lsm = LSM9DS1_I2C(i2c)
        self.bme = Adafruit_BME280_I2C(i2c)
        self.gps = None

        self.state = {'enabled': False, 'screen': 0}
        self.time = {'off': 0, 'update': 0, 'temp': 0, 'gps': 0, 'lsm': 0}
        # set times to non zero to start sensor monitoring

        self.lsmd = {'acc': [0, 0, 0], 'mag': [0, 0, 0], 'gyr': [0, 0, 0]}
        self.bmed = {'tmp': 99, 'hum': -1, 'prs': 0, 'dew': -1}
        self.gspd = {
            'spd': -1, 'crs': 400,
            'latd': 99, 'latm':0, 'latc': 'Z',
            'lond': 400, 'lonm':0, 'lonc': 'Z'}
        
        # fake data
        self.gpsd = {
            'spd': 2.3, 'crs': 22.5,
            'latd': 43, 'latm': 46.3043, 'latc': 'N',
            'lond': 79, 'lonm': 25.8343, 'lonc': 'W'}
        
    def set_time(self, name):
        self.time[name] = time() + _TIME[name]

    def check_time(self, name, when=time()):
        if self.time[name] > 0:
            if when > self.time[name]:
                return True
        return False

    def screen_0(self):
        self.lcd.set_cursor(0, 0)
        self.lcd.print("Spd {spd:5.2f}".format(**self.gpsd))
        self.lcd.set_cursor(11, 0)
        self.lcd.print("Crs {crs:5.1f}".format(**self.gpsd))
        self.lcd.set_cursor(0, 1)
        self.lcd.print(_LATF.format(**self.gpsd))
        self.lcd.set_cursor(0, 2)        
        self.lcd.print(_LONF.format(**self.gpsd))
        self.lcd.set_cursor(0, 3)
        ltime = datetime.now()
        self.lcd.print(ltime.strftime("%Y-%m-%dT%H:%M:%S"))

    def screen_1(self):
        self.lcd.print("Screen {}".format(self.state['screen']))
        # GPS SPD AND COURSE
        #print("Acceleration: ({0:0.3f},{1:0.3f},{2:0.3f}) m/s^2".format(*accel)#)
 #       print("Magetometer: ({0:0.3f},{1:0.3f},{2:0.3f}) gaus".format(*magn))
  #      print("Gyro: ({0:0.3f},{1:0.3f},{2:0.3f}) deg/s".format(*gyro))

    def screen_2(self):
        # WEATHER
        self.lcd.print("Screen {}".format(self.state['screen']))    
    
    def display(self):
        scrns = [screen_0, screen_1, screen_2]
        self.lcd.display()
        self.lcd.backlight()
        self.lcd.clear()
        scrns[self.state['screen']]()
        self.set_time('off')
        self.set_time('update')

    def update(self):
        print('update')

    def get_temp(self):
        print('get temp')

    def get_gps(self):
        print('get gps')
        
    def get_lsm(self):
        print('get lsm')
    
    def run_real(self):
        checks = {
            'temp': self.get_temp,
            'gps': self.get_gps,
            'lsm': self.get_lsm
            }
        while True:
            now = time()
            if self.pbut.pressed():
                if self.state['enabled']:
                    self.state['screen'] += 1
                    self.state['screen'] %= _SCREEN_MAX
                else:
                    self.state['enabled'] = True
                self.display()
            if self.check_time('off', now):
                self.lcd.backlight(False)
                self.lcd.display(False)
                self.time['off'] = 0
                self.state['enabled'] = False
                # reset screen to zero if has gone off
                self.state['screen'] = 0
            if self.state['enabled']:
                if self.check_time('update'):
                    self.update()
            for check in checks:
                if self.check_time(check, now):
                    checks[check]()
            sleep(_SLEEP)

    def clean_up(self):
        print("clean up")
        self.lcd.backlight(False)
        self.lcd.display(False)            
            
    def run(self):
        try:
            self.run_real()
        except Exception as e:
            print("Exception")
            self.clean_up()
            raise(e)
        finally:
            self.clean_up()                
        
if __name__ == '__main__':
    boat_sense = BoatSense()
    boat_sense.run()
