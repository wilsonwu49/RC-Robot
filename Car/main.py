# Listener (central)

from BLE_CEEO import Listen
import time
import json
import math

from machine import Pin, SoftI2C
import neopixel
import veml6040
from Motor import Motor

from color_samples import SAMPLES

# listener setup
NAME = "Wilany" # must match the yeller's name
buffer = b""
rainbow_now = False
last_l = 0
last_r = 0

L_FWD = 1
R_FWD = 0

def callback(data):
    # Pieces arrive in up to 20-byte chunks; a newline ends each message
    global buffer, last_l, last_r
    buffer += data
    while b"\n" in buffer:
        line, buffer = buffer.split(b"\n", 1)
        msg = json.loads(line.decode())
        last_l = msg.get("l")
        last_r = msg.get("r")

def goRainbow():
    print("Button pressed!")
    ccount = 0
    while ccount < len(rainbow):
        lights[0] = lights[1] = rainbow[ccount]
        lights.write()
        time.sleep(1)
        ccount +=1


def read_color():
    red, green, blue, white = sensor.read_rgbw()
    return red, green, blue, white

def normalize(r, g, b):
    # Each color as a share of the total, so r + g + b = 1
    total = r + g + b
    if total == 0:
        return (0.0, 0.0, 0.0)
    return (r / total, g / total, b / total)
        
def k_nearest_neighbor(x, y, z, k):
    distances = []
    for d in data:
        dist = math.sqrt((x - d[0]) ** 2 + (y - d[1]) ** 2 + (z - d[2]) ** 2)
        distances.append((dist, d[3]))   # d[3] is the color name now
 
    distances.sort()
    nearest = distances[:min(k, len(distances))]
    classes = [label for dist, label in nearest]
#     print("k nearest:", classes)
 
    return max(set(classes), key=classes.count)

def set_wheel(m, fwd, speed):
    if speed == 0:
        m.stop()
    elif speed > 0:
        m.start(fwd, speed)
    else:
        m.start(1 - fwd, -speed)


# color sensor setup
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
sensor = veml6040.VEML6040(i2c)
sensor.trigger_measurement()

left = Motor(12, 13, 39, 39)
right = Motor(14, 27, 39, 39)

# light color setup
lights = neopixel.NeoPixel(Pin(15), 2)
rainbow = [(20, 0, 0),
           (20, 5, 0),
           (20, 20, 0),
           (0, 20, 0),
           (0, 0, 20),
           (5, 0, 10),
           (10, 10, 10),
           (0, 0, 0)]
lights[0] = lights[1] = (10, 10, 10)
lights.write()

# Convert the saved samples to the same r, g, b shares (white cancels out)
data = []
for s in SAMPLES:
    rn, gn, bn = normalize(s[0], s[1], s[2])
    data.append((rn, gn, bn, s[4]))   # s[4] is the color name

p = None
try:
    p = Listen(NAME, verbose=False)
    p.callback = callback
    print("Looking for", NAME, "...")
    
    if p.connect_up():
        print("Connected")
        lights[0] = lights[1] = (0, 0, 0)
        lights.write()
        
        while p.is_connected:
            if rainbow_now:
                rainbow_now = False
                goRainbow()

            r, g, b, w = read_color()
            rn, gn, bn = normalize(r,g,b)
            result = k_nearest_neighbor(rn, gn, bn, 3)
            
            if result == "red":
                rainbow_now = True
            
            payload = json.dumps({"finish": rainbow_now}) + "\n"
            
            # Send in 20-byte pieces (the default packet size)
            for start in range(0, len(payload), 20):
                p.send(payload[start:start + 20])
                time.sleep_ms(20)
                
            print("left:",last_l,"right:",last_r)
            set_wheel(left, L_FWD, last_l)
            set_wheel(right, R_FWD, last_r)

            time.sleep(0.05)
    print("Lost connection")
finally:
    if p:
        p.disconnect()