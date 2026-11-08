from machine import Pin, ADC
import time

class Joystick:
    def __init__(self, pinx, piny, attenuation=ADC.ATTN_11DB):
        """
        Initialize the joystick with X, Y, and Switch (button) pins.
        - pin_x, pin_y: GPIO numbers connected to VRX and VRY
        - attenuation: 11dB allows full 0-3.3V range on ESP32 ADC
        """
        self.adcx = ADC(Pin(pinx))
        self.adcy = ADC(Pin(piny))
        
        # Set attenuation for full range reading (~3.3V)
        self.adcx.atten(attenuation)
        self.adcy.atten(attenuation)
        
        # Set resolution (ESP32 supports up to 12 bits: 0 - 4095)
        self.adcx.width(ADC.WIDTH_12BIT)
        self.adcy.width(ADC.WIDTH_12BIT)
        
        self.centerx = 32000
        self.centery = 32000
        self.deadzone = 3000
        
    def read(self):
        return self.adcx.read_u16(), self.adcy.read_u16()
    
    def scaled_read(self, scale=100):
        x, y = self.read()
        diffx = x - self.centerx
        diffy = y - self.centery
        
        outputx = 0 if abs(diffx) < self.deadzone else int((diffx / 13000) * scale)
        outputy = 0 if abs(diffy) < self.deadzone else int((diffy / 13000) * scale)
        
        outputx = max(-scale, min(scale, outputx))
        outputy = max(-scale, min(scale, outputy))

        
        return outputx, outputy

    