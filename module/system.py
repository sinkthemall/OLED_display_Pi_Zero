from interface import projector, CarouselMenu, ListOption
import subprocess

def shutDown():
    subprocess.run(f"sudo poweroff", shell=True)

def reboot():
    subprocess.run(f"sudo reboot", shell=True)

import socket
import psutil

def getLocalIP():
    interfaces = psutil.net_if_addrs()
    ip_addresses = {}
    ip_list = []
    for interface, addresses in interfaces.items():
        for address in addresses:
                if address.family == socket.AF_INET:  # IPv4
                    ip_list.append(f"{interface} - {address.address}")
                    # projector.Reset()
                    # # projector.DrawText((34, 10), f"Device IP:")
                    # # projector.DrawText((20, 26), f"{address.address}")
                    # projector.CenterText(10, f"Device IP:")
                    # projector.CenterText(26, f"{address.address}")
                    # # projector.DrawText((28, 1), f"Device IP: {address.address}")
                    # projector.Display(waitforkey= True)
                    # return
    ls = ListOption()
    ls.Interactive(ip_list)
    return 

SystemOptions = CarouselMenu({
    "Shutdown" : shutDown, 
    "Reboot" : reboot, 
    "Device IP"  : getLocalIP
}, isBase=False)