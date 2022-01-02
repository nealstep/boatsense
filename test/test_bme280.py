#!/usr/bin/env python3
#

from adafruit_bme280.basic import Adafruit_BME280_I2C
from board import I2C
from math import log
from time import sleep

i2c = I2C()
bme280 = Adafruit_BME280_I2C(i2c)
b = 17.62
c = 243.12

while True:
    temp = bme280.temperature
    humid = bme280.humidity
    press = bme280.pressure
    gamma = (b * temp / (c + temp)) + log(humid / 100.0)
    dewp = (c * gamma) / (b - gamma)

    print("Temperature: {:5.1f} C".format(temp))
    print("Humidity: {:5.1f} %".format(humid))
    print("Pressure: {:6.1f} hPa".format(press))
    print("Dew Point: {:5.1f} C".format(dewp))

    sleep(1)
