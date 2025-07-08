import subprocess
import re
from interface import keyboard, ListOption, projector, CarouselMenu
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

def profileRemove():
    while True:
        profile_list = scanProfileSSID()
        ls = ListOption()
        ls.LoadItems(profile_list, prompt = "Available profiles")
        ssid = ls.Interactive()
        if ssid == None:
            return 
        ls.LoadItems(["yes", "no"], prompt = "Delete profile?")
        ensure = ls.Interactive()
        if ensure == 0:
            try:
                subprocess.run(["sudo", "nmcli", "connection", "delete", profile_list[ssid]], check=True)
            except:
                # print("[x] Failed to remove profile")
                continue
        else:
            continue
def apConnect(ssid):
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
                subprocess.run(f"sudo nmcli dev wifi connect \"{ssid}\" password \"{pwd}\"",shell=True,  check=True)
                projector.Reset()
                projector.DrawText((1,28), f"[+] Wifi connected")
                projector.Display()
            except:
                projector.Reset()
                projector.DrawText((1,28), f"[x] Cannot connect wifi")
                projector.Display()

def wifiConnect():
    
    ls = ListOption()
    ap_list = scanAP()
    ls.LoadItems(ap_list, prompt="Available AP")
    ssid = ls.Interactive()
    if ssid == None:
        return 
    else:
        apConnect(ap_list[ssid])

def listAPInfo():
    try:
        output = subprocess.check_output(["nmcli", "-g", "SSID,SECURITY,FREQ,BARS", "dev", "wifi"], text=True)
        # print(output)
        tmp  = output.split("\n")
        AP_name = []
        AP_sec = []
        AP_freq = []
        AP_strength = []
        for i in tmp:
            if i != "":
                ssid, sec, freq, strength = i.split(":")
                AP_name.append(ssid)
                AP_sec.append(sec)
                AP_freq.append(freq)
                AP_strength.append(strength)
        ls = ListOption()
        while True: 
            ls.LoadItems(AP_name, prompt ="AP list")
            ssid = ls.Interactive()
            if ssid != None:
                projector.Reset()
                projector.DrawText((1, 1), f"SSID:")
                projector.DrawText((1, 13), f"{AP_name[ssid]}")
                projector.DrawText((1, 25), f"Freq: {AP_freq[ssid]}")
                projector.DrawText((1, 37), f"Security: {AP_sec[ssid]}")
                projector.DrawText((1, 49), f"Strength: {AP_strength[ssid]}")
                projector.Display(waitforkey=True)
                pass
            else:
                return 
    except:
        pass
    pass


WifiOptions = CarouselMenu({
    "Remove Profile" : profileRemove,
    "Connect AP" :wifiConnect,
    "Network Info" : listAPInfo
}, isBase=False)