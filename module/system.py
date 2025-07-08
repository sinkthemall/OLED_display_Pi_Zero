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
                    if (len(interface) > 2):
                        ip_list.append(f"{interface[0] + interface[-1]} - {address.address}") 
                    else:
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
    ls.LoadItems(ip_list, prompt="IP list")
    ls.Interactive()
    return 

SystemOptions = CarouselMenu({
    "Shutdown" : shutDown, 
    "Reboot" : reboot, 
    "Device IP"  : getLocalIP
}, isBase=False)