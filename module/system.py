from interface import projector
import subprocess

def ShutDown():
    subprocess.run(f"sudo poweroff", shell=True)

def Reboot():
    subprocess.run(f"sudo reboot", shell=True)

import socket
import psutil

def GetLocalIP():
    interfaces = psutil.net_if_addrs()
    ip_addresses = {}
    
    for interface, addresses in interfaces.items():
        if interface == "wlan0":
            for address in addresses:
                if address.family == socket.AF_INET:  # IPv4
                    projector.Reset()
                    # projector.DrawText((34, 10), f"Device IP:")
                    # projector.DrawText((20, 26), f"{address.address}")
                    projector.CenterText(10, f"Device IP:")
                    projector.CenterText(26, f"{address.address}")
                    # projector.DrawText((28, 1), f"Device IP: {address.address}")
                    projector.Display(waitforkey= True)
                    return
        
    return 

