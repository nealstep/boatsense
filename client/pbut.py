#!/usr/bin/env python3
#

from board import D11
from time import time

_BOUNCE = 0.05

class PBut:

    def __init__(self):
        D11.init(mode=D11.IN)
        self.last_time = 0
        self.last_state = D11.value()

    def pressed(self):
        ret = False
        state = D11.value()
        if state != self.last_state:
            now = time()
            if (now - self.last_time) > _BOUNCE:
                if state:
                    ret = True
                self.last_time = now
                self.last_state = state
        return ret

if __name__ == "__main__":
    from time import sleep
    _SLEEP = 0.05
    pbut = PBut()
    while True:
        if pbut.pressed():
            print("Pressed")
        sleep(_SLEEP)
