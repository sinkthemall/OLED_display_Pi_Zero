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
from module.wifi import WifiConnect, ProfileRemove
from module.system import ShutDown, Reboot, GetLocalIP
carousel = CarouselMenu(io, {
                                "Wifi" : {"Remove profile" : ProfileRemove, "Connect wifi" : WifiConnect}, 
                                "System": {"Shutdown" : ShutDown, "Reboot" : Reboot, "Device IP"  : GetLocalIP} , 
                                "Debug" : nothing, 
                                "Attack" : nothing, 
                                "Show Image" : test_drawImage}, isBase=True)
try:
    carousel.Interactive()
except:
    # print("Exitting ... ")
    io.GPIO_cleanup()
    exit(0)
