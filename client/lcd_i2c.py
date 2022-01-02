#!/usr/bin/env python3

from time import sleep
from micropython import const

# default address
_LCD_ADDRESS = const(0x27)
_LCD_COLS = const(20)
_LCD_ROWS = const(4)

# commands
_LCD_CLEARDISPLAY = const(0x01)
_LCD_RETURNHOME = const(0x02)
_LCD_ENTRYMODESET = const(0x04)
_LCD_DISPLAYCONTROL = const(0x08)
_LCD_CURSORSHIFT = const(0x10)
_LCD_FUNCTIONSET = const(0x20)
_LCD_SETCGRAMADDR = const(0x40)
_LCD_SETDDRAMADDR = const(0x80)

# flags for display entry mode
_LCD_ENTRYRIGHT = const(0x00)
_LCD_ENTRYLEFT = const(0x02)
_LCD_ENTRYSHIFTINCREMENT = const(0x01)
_LCD_ENTRYSHIFTDECREMENT = const(0x00)

# flags for display on/off control
_LCD_DISPLAYON = const(0x04)
_LCD_DISPLAYOFF = const(0x00)
_LCD_CURSORON = const(0x02)
_LCD_CURSOROFF = const(0x00)
_LCD_BLINKON = const(0x01)
_LCD_BLINKOFF = const(0x00)

# flags for display/cursor shift
_LCD_DISPLAYMOVE = const(0x08)
_LCD_CURSORMOVE = const(0x00)
_LCD_MOVERIGHT = const(0x04)
_LCD_MOVELEFT = const(0x00)

# flags for function set
_LCD_8BITMODE = const(0x10)
_LCD_4BITMODE = const(0x00)
_LCD_2LINE = const(0x08)
_LCD_1LINE = const(0x00)
_LCD_5x10DOTS = const(0x04)
_LCD_5x8DOTS = const(0x00)

# flags for backlight control
_LCD_BACKLIGHT = const(0x08)
_LCD_NOBACKLIGHT = const(0x00)

# bits
_En = const(0b00000100) # Enable bit
_Rw = const(0b00000010) # Read/Write bit
_Rs = const(0b00000001) # Register select bit

# constants
_ROW_OFFSETS = (0x00, 0x40, 0x14, 0x54)



class LCD_I2C:

    def __init__(self, i2c, address=_LCD_ADDRESS, cols=20, rows=4):
        self.i2c = i2c
        self.address = address
        self.cols = cols
        self.rows = rows
        # set state variables
        self.backlightval = _LCD_NOBACKLIGHT
        self.displayfunction = _LCD_4BITMODE | _LCD_1LINE | _LCD_5x8DOTS
        if self.rows > 1:
            self.displayfunction |= _LCD_2LINE
        self.numlines = self.rows
        sleep(0.05)
        self.expander_write(self.backlightval)
        sleep(1)
        # try and get into 4 bit mode
        for i in range(3):
            sleep(0.005)
            self.write4Bits(0x03 << 4)
        sleep(0.0002)
        self.write4Bits(0x02 << 4)
        # initialize
        self.command(_LCD_FUNCTIONSET | self.displayfunction)
        self.displaycontrol= _LCD_DISPLAYON | _LCD_CURSOROFF | _LCD_BLINKOFF
        self.display()
        self.clear()
        self.displaymode = _LCD_ENTRYLEFT | _LCD_ENTRYSHIFTDECREMENT
        self.command(_LCD_ENTRYMODESET | self.displaymode)
        self.home()

    # writing routines
    def expander_write(self, value):
        self.i2c.writeto(self.address, bytes([value | self.backlightval]))

    def pulseEnable(self, value):
        self.expander_write(value | _En) # En high
        sleep(0.000001) # enable pulse must be >450ns
        self.expander_write(value & ~_En) # En low
        sleep(0.00005)
    
    def write4Bits(self, value):
        self.expander_write(value)
        self.pulseEnable(value)

    def send(self, value, mode):
        highnib = value & 0xf0
        lownib= (value << 4) & 0xf0
        self.write4Bits(highnib | mode)
        self.write4Bits(lownib | mode)
        
    def write(self, value):
        self.send(value, _Rs)
        
    def command(self, cmd):
        self.send(cmd, 0)

    def putc(self, value):
        self.write(ord(value))
        
    # functions
    def display(self, active=True):
        if active:
            self.displaycontrol |= _LCD_DISPLAYON
        else:
            self.displaycontrol &= ~_LCD_DISPLAYON
        self.command(_LCD_DISPLAYCONTROL | self.displaycontrol)

    def clear(self):
        self.command(_LCD_CLEARDISPLAY)
        sleep(0.002)
    
    def home(self):
        self.command(_LCD_RETURNHOME)
        sleep(0.002)

    def backlight(self, active=True):
        if active:
            self.backlightval = _LCD_BACKLIGHT
        else:
            self.backlightval = _LCD_NOBACKLIGHT
        self.expander_write(0)

    def cursor(self, active=True):
        if active:
            self.displaycontrol |= _LCD_CURSORON
        else:
            self.displaycontrol &= ~_LCD_CURSORON
        self.command(_LCD_DISPLAYCONTROL | self.displaycontrol)

    def blink(self, active=True):
        if active:
            self.displaycontrol |= _LCD_BLINKON
        else:
            self.displaycontrol &= ~_LCD_BLINKON
        self.command(_LCD_DISPLAYCONTROL | self.displaycontrol)

    def set_cursor(self, col, row):
        if row > self.numlines:
            row = selfnumlines - 1
        self.command(_LCD_SETDDRAMADDR | (col + _ROW_OFFSETS[row]))

    def scroll_display(self, left=True):
        if left:
            cmd = _LCD_CURSORSHIFT | _LCD_DISPLAYMOVE | _LCD_MOVELEFT
        else:
            cmd = _LCD_CURSORSHIFT | _LCD_DISPLAYMOVE | _LCD_MOVERIGHT
        self.command(cmd)
        
    def text_flow(self, left=True):
        if left:
            self.displaymode |= LCD_ENTRYLEFT
        else:
            self.displaymode &= ~LCD_ENTRYLEFT
        self.command(LCD_ENTRYMODESET | self.displaymode)

    def autoscroll(self, active=True):
        if active:
            self.displaymode |= LCD_ENTRYSHIFTINCREMENT
        else:
            self.displaymode &= ~LCD_ENTRYSHIFTINCREMENT;
        self.command(LCD_ENTRYMODESET | self.displaymode);

    def create_char(self, location, charmap):
        location &= 0x7 # we only have 8 locations 0-7
        self.command(_LCD_SETCGRAMADDR | (location << 3))
        for i in range(8):
            self.write(charmap[i])

    def printByte(self, value):
        self.write(value)
            
    def print(self, value):
        for ch in value:
            self.putc(ch)
    

if __name__ == "__main__":
    from board import I2C

    bell  = (0x4,0xe,0xe,0xe,0x1f,0x0,0x4,0x0)
    note  = (0x2,0x3,0x2,0xe,0x1e,0xc,0x0,0x0)
    clock = (0x0,0xe,0x15,0x17,0x11,0xe,0x0,0x0)
    heart = (0x0,0xa,0x1f,0x1f,0xe,0x4,0x0,0x0)
    duck  = (0x0,0xc,0x1d,0xf,0xf,0x6,0x0,0x0)
    check = (0x0,0x1,0x3,0x16,0x1c,0x8,0x0,0x0)
    cross = (0x0,0x1b,0xe,0x4,0xe,0x1b,0x0,0x0)
    retarrow = (0x1,0x1,0x5,0x9,0x1f,0x8,0x4,0x0)
    
    i2c = I2C()
    lcd = LCD_I2C(i2c)
    lcd.backlight()

    lcd.create_char(0, bell)
    lcd.create_char(1, note)
    lcd.create_char(2, clock)
    lcd.create_char(3, heart)
    lcd.create_char(4, duck)
    lcd.create_char(5, check)
    lcd.create_char(6, cross)
    lcd.create_char(7, retarrow)
    lcd.home()

    lcd.set_cursor(0, 0);
    for i in range(20):
        lcd.printByte(6);
    lcd.set_cursor(0, 1);
    lcd.printByte(6);
    lcd.print("   Hello world    ");
    lcd.printByte(6);
    lcd.set_cursor(0, 2);
    lcd.printByte(6);
    lcd.print("  i ");
    lcd.printByte(3);
    lcd.print(" arduinos!   ");
    lcd.printByte(6);
    lcd.set_cursor(0, 3);
    for i in range(20):
        lcd.printByte(6);
    sleep(1)
    lcd.home()
    for i in range(4):
        lcd.scroll_display()
        sleep(0.5)
    sleep(0.5)
    for i in range(4):
        lcd.scroll_display(False)
        sleep(0.5)

        
    
