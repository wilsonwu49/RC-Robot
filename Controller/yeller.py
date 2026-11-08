# Yeller (peripheral)

from BLE_CEEO import Yell
from machine import Pin
from time import ticks_ms, ticks_diff
import time
import json
import math

from color_samples import SAMPLES

NAME = "Wilany"
buffer = b""

btn = Pin(34, Pin.IN, Pin.PULL_UP) 
DEBOUNCE_MS = 200
last_press = 0


def normalize(r, g, b):
    # Each color as a share of the total, so r + g + b = 1
    total = r + g + b
    if total == 0:
        return (0.0, 0.0, 0.0)
    return (r / total, g / total, b / total)


# Convert the saved samples to the same r, g, b shares (white cancels out)
data = []
for s in SAMPLES:
    rn, gn, bn = normalize(s[0], s[1], s[2])
    data.append((rn, gn, bn, s[4]))   # s[4] is the color name


def button_handler(pin):
    global last_press
    now = ticks_ms()
    if ticks_diff(now, last_press) > DEBOUNCE_MS:
        if (pin.value() == 0):
            last_press = now
            print("Button pressed!")
            payload = json.dumps({"from": "yeller", "count": 1}) + "\n"
            # Send in 20-byte pieces (the default packet size)
            for start in range(0, len(payload), 20):
                p.send(payload[start:start + 20])
                time.sleep_ms(20)


btn.irq(trigger=Pin.IRQ_FALLING, handler=button_handler)


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
            
        
        
def k_nearest_neighbor(x, y, z, k):
    distances = []
    for d in data:
        dist = math.sqrt((x - d[0]) ** 2 + (y - d[1]) ** 2 + (z - d[2]) ** 2)
        distances.append((dist, d[3]))   # d[3] is the color name now
 
    distances.sort()
    nearest = distances[:min(k, len(distances))]
    classes = [label for dist, label in nearest]
    print("k nearest:", classes)
 
    return max(set(classes), key=classes.count)


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