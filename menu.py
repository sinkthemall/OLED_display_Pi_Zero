from interface import CarouselMenu, KeyBoard
from iohandler import InputHandler, ScreenManager
import subprocess
import re

def scanAP():
    """Scan for Wi-Fi networks and print SSIDs."""
    try:
        output = subprocess.check_output("sudo iwlist wlan0 scan", shell=True).decode()
        ssids = re.findall(r'ESSID:"([^"]+)"', output)
        print("\nAvailable Wi-Fi Networks:")
        return [ssid if ssid else "[Hidden SSID]" for ssid in ssids]
    except Exception as e:
        return []

class WifiModule:
    def __init__(self):
        self.keyboard = KeyBoard(InputHandler(), prompt="Enter password")
        self.AP = {}
        self.carousel = CarouselMenu(InputHandler(), self.AP, isBase=False)
    def Connect(self):
        pass
    def MainOperation(self):
        
        while True:
            self.AP = scanAP()
            option = self.carousel.Interactive()
            if option == None:
                break
            elif option != None:
                self.keyboard.Interactive()
                

# a demo menu
def Menu():
    ui = CarouselMenu(InputHandler(), ["Wifi", "Shutdown", "System", ], isBase=True)
    while True: 
        option = ui.Interactive()
        if option == "Shutdown":
            pass
        elif option == "Wifi":
            pass
        elif option == "System":
            pass
        else:
            continue
