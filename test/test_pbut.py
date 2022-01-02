#!/usr/bin/env python3


from board import D11
from time import time, sleep

_BOUNCE = 0.05
_SLEEP = 0.05

D11.init(mode=D11.IN)

last_time = 0
last_state = D11.value()

while True:
    state = D11.value()
    if state != last_state:
        now = time()
        if (now - last_time) > _BOUNCE:
            if state:
                print("Pressed")
            last_state = state
            last_time = now
    sleep(_SLEEP)
