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
        if len(cls._instance.screencontainer) == 0:
            return
        else:
            cls._instance.screencontainer.pop()
        # cls.DisplayImage()


font_size = 11
font = ImageFont.truetype("UbuntuMono-B.ttf", size=font_size)



'''
The InputHandler still don't handle the case where multiple buttons are pressed in the same time.
Maybe make a mutex to limit only 1 button is press at the time?
'''
class InputHandler:
    _instance = None  # Singleton instance
    actionStack = None
    actionIdx = None
    def __new__(cls, bus_speed_hz=8000000):
        if cls._instance is None:
            cls._instance = super(InputHandler, cls).__new__(cls)
            cls._instance.__initialize(bus_speed_hz)  # Call a private method for initialization
        return cls._instance

    def __initialize(self, bus_speed_hz):
        """
        Private initialization method to prevent re-initialization when creating new instances.
        """
        self.pinout = {
            JS_L_PIN: 0,
            JS_R_PIN: 1,
            JS_U_PIN: 2,
            JS_D_PIN: 3,
            JS_P_PIN: 4,
            BTN1_PIN: 5,
            BTN2_PIN: 6,
            BTN3_PIN: 7
        }


        # Max depth action stack is 16
        self.actionStack = [[None for i in range(16)] for j in range(len(self.pinout))]
        self.actionIdx = -1
        # self.iBuf = [None for _ in range(8)]  # Buffer for key presses
        self.lastVal = -1
        self.mutex = threading.Lock()
        self.__GPIO_PinInitialize()

    # def GetCurrentKeyPress(self):
    #     """
    #     Return the current key press in BCM pin value.
    #     """
    #     with self.mutex:
    #         if self.start_idx == self.end_idx:
    #             return None
    #         else:
    #             val = self.iBuf[self.start_idx]
    #             self.start_idx += 1
    #             self.start_idx %= 8
    #             return val

    # def InputBuffering(self, channel):
    #     """
    #     Store key press events in buffer.
    #     """
    #     with self.mutex:
    #         self.iBuf[self.end_idx] = channel
    #         self.end_idx += 1
    #         self.end_idx %= 8

    def Nothing(self):
        '''
        Do nothing, for button that is not in mapper
        '''
        return 

    def ActionTrigger(self, channel):
        # Currently, lastval isn't necessary
        # with self.mutex:
        #     if self.lastVal == -1:
        #         self.lastVal = channel
        #     else:
        #         return
        if self.actionIdx >=0:
            self.actionStack[self.pinout[channel]][self.actionIdx]()
        # self.lastVal = -1


    def PushInterface(self, mapper : dict ):
        
        self.actionIdx += 1

        # do a check mapper before adding, won't harm performance
        for button in mapper:
            if not (button in self.pinout):
                # print("[-] Invalid button number!")
                exit(-1)

        for pin, idx in self.pinout.items():
            if not (pin in mapper):
                self.actionStack[idx][self.actionIdx] = self.Nothing
            else:
                self.actionStack[idx][self.actionIdx] = mapper[pin]
        
        # print("[+] Interface pushed")


    def PopInterface(self ):
        self.actionIdx -= 1
        # print("[+] Interface popped")


    def __GPIO_PinInitialize(self):
        """
        Initialize GPIO pins.
        """
        GPIO.setmode(GPIO.BCM)
        for pin in self.pinout:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(pin, GPIO.FALLING, callback=self.ActionTrigger, bouncetime=200)

    def GPIO_cleanup(self):
        """
        Clean up GPIO pins.
        """
        GPIO.cleanup()


io = InputHandler()
screen = ScreenManager()