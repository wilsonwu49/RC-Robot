from joystick import Joystick
from Motor import Motor
import time

MAX_SPEED = 60
L_FWD = 1
R_FWD = 0

joy = Joystick(pinx=25, piny=33)
left = Motor(12, 13, 39, 39)
right = Motor(14, 27, 39, 39)


def set_wheel(m, fwd, speed):
    if speed == 0:
        m.stop()
    elif speed > 0:
        m.start(fwd, speed)
    else:
        m.start(1 - fwd, -speed)


try:
    while True:
        jx, jy = joy.scaled_read()
        l = max(-100, min(100, jy + jx)) * MAX_SPEED // 100
        r = max(-100, min(100, jy - jx)) * MAX_SPEED // 100
        set_wheel(left, L_FWD, l)
        set_wheel(right, R_FWD, r)
        print(f"Joystick: x = {jx}, y = {jy}   left = {l}, right = {r}")
        time.sleep_ms(20)
finally:
    left.stop()
    right.stop()
