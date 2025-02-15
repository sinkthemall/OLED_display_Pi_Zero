import subprocess
import re
from interface import keyboard, ListOption, projector
from iohandler import io, screen
import time
def scanAP():
    """Scan for Wi-Fi networks and print SSIDs."""
    try:
        output = subprocess.check_output("sudo iwlist wlan0 scan", shell=True).decode()
        ssids = re.findall(r'ESSID:"([^"]+)"', output)
        # print("\nAvailable Wi-Fi Networks:")
        val = []
        for ssid in ssids:
            if ssid :
                val.append(ssid)

        return val
    except Exception as e:
        return []
def scanProfileSSID():
    try:
        # Run nmcli command to list all saved connections
        output = subprocess.check_output(["nmcli", "-t", "-f", "NAME,TYPE", "connection"], text=True)

        profiles = []
        for line in output.splitlines():
            name, conn_type = line.split(":")
            if conn_type.strip() == "802-11-wireless":  # Filter only Wi-Fi profiles
                profiles.append(name)

        if not profiles:
            return []
        else:
            # print("Saved Wi-Fi Profiles:")
            ssids = []
            for profile in profiles:
                # Get SSID associated with the profile
                ssid_output = subprocess.check_output(["nmcli", "-g", "802-11-wireless.ssid", "connection", "show", profile], text=True).strip()
                ssids.append(ssid_output)
            return ssids
    except subprocess.CalledProcessError as e:
        return []
def profile_existed(ssid):
    try:
        output = subprocess.check_output(["sudo", "nmcli", "connection", "show"], text=True)
        if ssid in output:
            # print("True")
            return True  

        else:
            # print("False")
            return False
    except subprocess.CalledProcessError as e :
        # print("Error")
        return False

def ProfileRemove():
    while True:
        profile_list = scanProfileSSID()
        ssid = ListOption(inp = io).Interactive(profile_list)
        if ssid == None:
            return 
        ensure = ListOption(inp = io).Interactive(["yes", "no"], "Delete profile?", yesno = True)
        if ensure == "yes":
            try:
                subprocess.run(["sudo", "nmcli", "connection", "delete", ssid], check=True)
            except:
                # print("[x] Failed to remove profile")
                continue
        else:
            continue
def APConnect(ssid):
    if profile_existed(ssid):
        print("[+] Profiled existed")
        try:
            subprocess.run(["sudo", "nmcli", "dev", "wifi", "connect", ssid], check = True )
        except:
            projector.Reset()
            projector.DrawText((1,28), f"[x] Cannot connect wifi")
            projector.Display()
            # print("[x] Cannot connect to wifi!")
    else:
        keyboard.Interactive(prompt="Enter password")
        pwd = keyboard.GetVal()
        # print(pwd)
        if pwd == None:
            # print("[*] Aborted!")
            return
        else:
            try:
                subprocess.run(f"sudo nmcli dev wifi connect {ssid} password {pwd}",shell=True,  check=True)
                projector.Reset()
                projector.DrawText((1,28), f"[+] Wifi connected")
                projector.Display()
            except:
                projector.Reset()
                projector.DrawText((1,28), f"[x] Cannot connect wifi")
                projector.Display()

def WifiConnect():
    
    ls = ListOption(inp = io)
    ap_list = scanAP()
    ssid = ls.Interactive(ap_list)
    if ssid == None:
        return 
    else:
        APConnect(ssid)