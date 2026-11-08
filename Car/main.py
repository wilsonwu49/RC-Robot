# Listener (central)

from BLE_CEEO import Listen
import time
import json

from machine import Pin, SoftI2C
import neopixel
import veml6040

# listener setup
NAME = "Wilany" # must match the yeller's name
buffer = b""
rainbow_now = False

def callback(data):
    # Pieces arrive in up to 20-byte chunks; a newline ends each message
    global buffer, rainbow_now
    buffer += data
    while b"\n" in buffer:
        line, buffer = buffer.split(b"\n", 1)
        msg = json.loads(line.decode())
        print("Received:", msg)
        if msg["from"] == "yeller":
            rainbow_now = True

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

def goRainbow():
    print("Button pressed!")
    ccount = 0
    while ccount < len(rainbow):
        lights[0] = lights[1] = rainbow[ccount]
        lights.write()
        time.sleep(1)
        ccount +=1

# color sensor setup
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
sensor = veml6040.VEML6040(i2c)
sensor.trigger_measurement()

def read_color(): # use example: r, g, b, w = read_color()
    
    r_sum = g_sum = b_sum = w_sum = 0
    red, green, blue, white = sensor.read_rgbw()
    r_sum += red
    g_sum += green
    b_sum += blue
    w_sum += white
    return r_sum, g_sum, b_sum, w_sum


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
            payload = json.dumps({"from": "listener", "r": r, "g": g, "b": b, "w": w}) + "\n"
            
            # Send in 20-byte pieces (the default packet size)
            for start in range(0, len(payload), 20):
                p.send(payload[start:start + 20])
                time.sleep_ms(20)

            time.sleep(1)
    print("Lost connection")
finally:
    if p:
        p.disconnect()