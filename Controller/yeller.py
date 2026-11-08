# Yeller (peripheral)

from BLE_CEEO import Yell
from machine import Pin
from time import ticks_ms, ticks_diff
import time
import json
import math
from joystick import Joystick


NAME = "Wilany"
buffer = b""


def callback(msg_data):
    # Pieces arrive in up to 20-byte chunks; a newline ends each message
    global buffer
    buffer += msg_data
    while b"\n" in buffer:
        line, buffer = buffer.split(b"\n", 1)
        msg = json.loads(line.decode())
        r = msg["r"]
        g = msg["g"]
        b = msg["b"]

        rn, gn, bn = normalize(r, g, b)
        #print("Norm R G B:", rn, gn, bn)
        result = k_nearest_neighbor(rn, gn, bn, 3)
        #print(">>> This color is: {} <<<\n".format(result.upper()))
        #colorFound = format(result.upper())
        #print(type(result))
        if result == "red":
            print("yeah dis is red")
            payload = json.dumps({"from": "yeller", "count": 1}) + "\n"
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