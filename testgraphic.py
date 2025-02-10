from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.core import lib

from luma.oled.device import sh1106
import RPi.GPIO as GPIO

from config import *

import time


from test import InputHandler
from PIL import ImageFont


serial = spi(device=0, port=0, bus_speed_hz = 8000000, transfer_size = 4096, gpio_DC = DC_PIN, gpio_RST = RST_PIN)
device = sh1106(serial, rotate=2) #sh1106


WIDTH = 128
HEIGHT = 64

GPIO.setmode(GPIO.BCM) 
GPIO.setup(JS_U_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(JS_D_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(JS_L_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(JS_R_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(JS_P_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(BTN1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(BTN2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(BTN3_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up


# draw = canvas(device)

# draw.text((1,1), "Hello", fill = 255)
font_size = 11
font = ImageFont.truetype("UbuntuMono-BI.ttf", size=font_size)

def changetext(key):
    with canvas(device) as draw:
        draw.text((1,1), f"[*] {str(key.ascii_lowercase())}", fill = 255, font= font)

# time.sleep(10)
input_handler = InputHandler(changetext)
try:
    while True: 
        time.sleep(0.5)
except KeyboardInterrupt:
    print("Exiting...")
    input_handler.cleanup()