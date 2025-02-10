from luma.core.interface.serial import spi 
from luma.core.render import canvas
from luma.oled.device import sh1106
from config import *
from PIL import ImageFont, Image
import threading
import RPi.GPIO as GPIO


from collections import deque
class ScreenManager:
    _instance = None
    def __new__(cls, bus_speed_hz = 8000000):
        if cls._instance is None:
            # print("Instance created!")
            cls._instance = super(ScreenManager, cls).__new__(cls)
            cls._instance.serial = spi(device = 0, port = 0, bus_speed_hz=bus_speed_hz, transfer_size=4096, 
                                       gpio_DC= DC_PIN, gpio_RST= RST_PIN)
            cls._instance.device = sh1106(cls._instance.serial, rotate= 2)
            cls._instance.screencontainer = deque()
        return cls._instance
    @classmethod
    def DisplayImage(cls):
        '''
        Display image on top stack, this one assumeee all sent image is in the size 128x64
        '''
        # print("Display!")
        if cls._instance == None:
            return
        if len(cls._instance.screencontainer) == 0:
            return
        cls._instance.device.display(cls._instance.screencontainer[-1])


    @classmethod
    def InitializeSession(cls, img ):
        '''
        Add image to stack
        '''
        # print("Pushed!")
        if cls._instance == None:
            return
        cls._instance.screencontainer.append(img)

    @classmethod
    def EndSession(cls):
        '''
        Pop image from stack
        '''
        if cls._instance == None:
            return
        if len(cls._instance.screencontainer):
            return
        else:
            cls._instance.screencontainer.pop()


font_size = 11
font = ImageFont.truetype("UbuntuMono-B.ttf", size=font_size)




class InputHandler:
    def __init__(self, bus_speed_hz = 8000000):
        # self.serial = spi(device=0, port = 0, bus_speed_hz=bus_speed_hz, transfer_size=4096, gpio_DC= DC_PIN, 
        #                   gpio_RST= RST_PIN)
        self.pinout = {
            "left" : JS_L_PIN,
            "right" : JS_R_PIN,
            "up" : JS_U_PIN,
            "down" : JS_D_PIN,
            "press" : JS_P_PIN,
            "btn1" : BTN1_PIN,
            "btn2" : BTN2_PIN,
            "btn3" : BTN3_PIN
        }

        # self.device = sh1106(self.serial, rotate=2)
        self.iBuf = [ None for i in range(8)] # Normally, no one can send more than 8 keystroke instancely
        # so I set buffer maxsize is 8 
        self.start_idx = 0
        self.end_idx = 0
        self.mutex = threading.Lock() 
        self.__GPIO_PinInitialize()
        pass
    # def DrawText(self, coor, textstr, font=font):
    #     with canvas(self.device) as draw:
    #         draw.text((coor[0], coor[1]), text=textstr, fill = 255, font=font)


    # def DrawImage(self, img):
    #     if img is None:
    #         return
        
    #     # Ensure image is in 1-bit monochrome mode
    #     img = img.convert("1")

    #     # Resize image to fit OLED (128x64)
    #     img_resized = img.resize((OLED_WIDTH, OLED_HEIGHT), Image.Resampling.LANCZOS)

    #     # Display image on OLED screen
    #     self.device.display(img_resized)
    #     pass

    def GetCurrentKeyPress(self):
        '''
        Return current key press in BCM pin value
        '''
        with self.mutex:
            if self.start_idx == self.end_idx:
                return None
            else:
                val = self.iBuf[self.start_idx]
                self.start_idx += 1
                self.start_idx %= 8
                return val
    
    def InputBuffering(self, channel):
        with self.mutex:
            self.iBuf[self.end_idx] = channel
            self.end_idx += 1
            self.end_idx %= 8

    def __GPIO_PinInitialize(self):
        '''
        Initializing GPIO pins
        '''

        GPIO.setmode(GPIO.BCM)
        for key, pin in self.pinout.items():
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(pin, GPIO.FALLING, callback=self.InputBuffering, bouncetime=200)

        pass

    def GPIO_cleanup(self):
        GPIO.cleanup()