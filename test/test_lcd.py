#!/usr/bin/env python3
#

from board import I2C
from datetime import datetime, timezone
from time import sleep

from lcd_i2c import LCD_I2C


i2c = I2C()
lcd = LCD_I2C(i2c)
lcd.backlight()

lcd.set_cursor(0, 0)
lcd.print('Lat   43{}46.3043 N'.format(chr(223)))
lcd.set_cursor(0, 1)
lcd.print('Long 079{}25.8343 W'.format(chr(223)))
lcd.set_cursor(0, 2)
ltime = datetime.now(timezone.utc)
gtime = ltime.replace(tzinfo=timezone.utc).astimezone(tz=None)
lcd.print(ltime.strftime("%Y-%m-%dT%H:%M:%S"))
lcd.set_cursor(0, 3)
lcd.print("12345678901234567890")
sleep(10)
lcd.display(False)
lcd.backlight(False)
