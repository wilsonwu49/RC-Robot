# Yeller (peripheral)

from BLE_CEEO import Yell
from machine import Pin
from time import ticks_ms, ticks_diff
from joystick import Joystick
import time
import json

NAME = "Wilany"
buffer = b""

MAX_SPEED = 60
#L_FWD = 1
#R_FWD = 0

joy = Joystick(pinx=25, piny=33)

def callback(msg_data):
    # Pieces arrive in up to 20-byte chunks; a newline ends each message
    global buffer
    buffer += msg_data
    while b"\n" in buffer:
        line, buffer = buffer.split(b"\n", 1)
        msg = json.loads(line.decode())
        jx, jy = joy.scaled_read()
        
        l = max(-100, min(100, jy - jx)) * MAX_SPEED // 100
        r = max(-100, min(100, jy + jx)) * MAX_SPEED // 100
        payload = json.dumps({"l": l, "r": r}) + "\n"
#         print({"l": l, "r": r})
        # Send in 20-byte pieces (the default packet size)
        for start in range(0, len(payload), 20):
            p.send(payload[start:start + 20])
            time.sleep_ms(20)
            

p = None
try:
    p = Yell(NAME, interval_us=30000, verbose=False)
    p.callback = callback

    print("Waiting for a listener...")
    if p.connect_up():
        print("Connected")
        while p.is_connected:
            time.sleep(1)
    print("Lost connection")
finally:
    if p:
        p.disconnect()