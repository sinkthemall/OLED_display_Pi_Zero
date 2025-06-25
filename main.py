from iohandler import InputHandler, ScreenManager
from config import *
import time 
from PIL import Image
from interface import CarouselMenu, projector

def test_drawImage():
    projector.Reset()
    projector.DrawImage("./new_nyancat.jpg", 1)
    projector.Display(waitforkey=True)



def nothing():
    pass
io = InputHandler()
# keyboard = KeyBoard(io)
from module.network import WifiOptions
from module.system import SystemOptions
carousel = CarouselMenu({
                                "Network" : WifiOptions.Interactive, 
                                "System": SystemOptions.Interactive , 
                                "Debug" : nothing, 
                                "Attack" : nothing, 
                                "Show Image" : test_drawImage
            }, isBase=True)
try:
    carousel.Interactive()
except:
    # print("Exitting ... ")
    io.GPIO_cleanup()
    exit(0)
