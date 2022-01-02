#!/usr/bin/env python3
#

from adafruit_lsm9ds1 import LSM9DS1_I2C
from board import I2C
from time import sleep

i2c = I2C()
sensor = LSM9DS1_I2C(i2c)

while True:
    accel = sensor.acceleration
    magn = sensor.magnetic
    gyro = sensor.gyro
    temp = sensor.temperature

    print("Acceleration: ({0:0.3f},{1:0.3f},{2:0.3f}) m/s^2".format(*accel))
    print("Magetometer: ({0:0.3f},{1:0.3f},{2:0.3f}) gaus".format(*magn))
    print("Gyro: ({0:0.3f},{1:0.3f},{2:0.3f}) deg/s".format(*gyro))
    print("Temperature: {:5.1f} C".format(temp))

    sleep(1)

