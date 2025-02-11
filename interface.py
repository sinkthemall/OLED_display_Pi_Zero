
from iohandler import InputHandler, ScreenManager
from config import *
from PIL import ImageDraw, Image, ImageFont
import time
keychoice = [
	["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"],
	["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"],
	["0","1","2","3","4","5","6","7","8","9","+","-","*","/","&","|","^","~","(",")","[","]","{","}","<",">"],
    ["!","@","#","$","%","_","=",";",":","'",'"',",",".","?","`","\\",]
]


font = ImageFont.truetype("UbuntuMono-B.ttf", size=14)
titlefont = ImageFont.truetype("UbuntuMono-R.ttf", size = 12)
carousel_font = ImageFont.truetype("Roboto-Medium.ttf", size = 11)
SLIDE_SIZE = 14
class KeyBoard:
    def __init__(self,  io : InputHandler, prompt = ""):
        pass
        self.buffer = [(0,0) for i in range(128)] # currently limit to 128 char
        self.index = 0
        if (len(prompt) > 20):
            self.prompt = prompt[:20] + ".."
        else:
            self.prompt = prompt
        self.io = io
        self.val = None
        self.image = Image.new("1", (OLED_WIDTH, OLED_HEIGHT), color = 0)
        self.draw = ImageDraw.Draw(self.image)
        self.screen = ScreenManager()
    def Interactive(self):
        self.screen.InitializeSession(self.image)
        while True: 
            keypress = self.io.GetCurrentKeyPress()
            if keypress == JS_L_PIN:
                # print("Key pressed: Left")
                self.__Left()
            elif keypress == JS_R_PIN:
                # print("Key pressed: Right")
                self.__Right()
            elif keypress == JS_U_PIN:
                # print("Key pressed: Up")
                self.__Up()
            elif keypress == JS_D_PIN:
                # print("Key pressed: Down")
                self.__Down()
            elif keypress == BTN1_PIN:
                # print("Key pressed: Btn1")
                self.__DelChar()
            elif keypress == JS_P_PIN:
                # print("Key pressed: Press")
                self.__AddChar()
            elif keypress == BTN3_PIN:
                self.val = None
                break
            elif keypress == BTN2_PIN:
                self.val = "".join(self.buffer[:self.index])
            time.sleep(0.05)
            self.__Display()
        self.screen.EndSession()
    def __DelChar(self):
        self.index -= 1
    def __AddChar(self):
        self.index += 1
        self.buffer[self.index] = (0,0)
    def __Up(self):
        x, y = self.buffer[self.index]
        if (x > 0):
            self.buffer[self.index] = (x - 1, y)
    def __Down(self):
        x, y = self.buffer[self.index]
        if (x < 3):
            if (y < len(keychoice[x + 1])):
                self.buffer[self.index] = (x + 1, y)
    def __Left(self):
        x, y = self.buffer[self.index]
        self.buffer[self.index] = (x, (y - 1) % len(keychoice[x]))
    def __Right(self):
        x, y = self.buffer[self.index]
        self.buffer[self.index] = (x, (y - 1) % len(keychoice[x]))
     
    def __Display(self):
        # image  = Image.new("1", (OLED_WIDTH, OLED_HEIGHT), color = 0)
        x = 1
        y = 26
        # draw = ImageDraw.Draw(self.image)
        self.draw.rectangle((0,0,OLED_WIDTH, OLED_HEIGHT), fill = 0)
        self.draw.text((1, 1), text = f"{self.prompt}", fill = 255, font= titlefont)
        st = 0
        if (self.index>= SLIDE_SIZE - 1):
            st = self.index - SLIDE_SIZE + 1
        for i in range(st, self.index + 1):
            keyx, keyy = self.buffer[i]
            self.draw.text((x, y), text=keychoice[keyx][keyy], fill=255, font = font)
            x += 9

        x -= 9
        self.draw.text((x, y + 3), text = "_", fill= 255, font = font)
        self.screen.DisplayImage()


class RangeAdjust:
    def __init__(self):
        pass

# Original CarouselMenu 
# class CarouselMenu:
#     def __init__(self, io : InputHandler, itemlist : list, isBase : False):
#         self.idx = 0
#         self.slider= 0 
#         self.items = itemlist
#         self.image = Image.new("1", (OLED_WIDTH, OLED_HEIGHT), color = 0)
#         self.io = io
#         self.draw = ImageDraw.Draw(self.image)
#         self.screen = ScreenManager()
#         self.isbase = isBase
#         pass
#     def Interactive(self):
#         self.screen.InitializeSession(self.image)
#         val = None
#         while True: 
#             keypress = self.io.GetCurrentKeyPress()
#             if keypress == JS_U_PIN:
#                 # print("Key pressed: Up")
#                 self.__Up()
#             elif keypress == JS_D_PIN:
#                 # print("Key pressed: Down")
#                 self.__Down()
#             elif keypress == BTN3_PIN:
#                 if not self.isbase:
#                     break
#             elif keypress == JS_P_PIN:
#                 val = self.items[self.idx + self.slider]
#                 break  
#             self.__Display()
#             time.sleep(0.05)
#         self.screen.EndSession()
#         return val

#     def __Up(self):
#         if (self.idx + self.slider == 0):
#             if len(self.items) > 4:
#                 self.slider = len(self.items) - 4
#                 self.idx = 3
#             else:
#                 self.idx = len(self.items) - 1
#                 self.slider = 0

#         elif (self.idx == 0):
#             self.slider -=1
#         else:
#             self.idx -= 1


#     def __Down(self):
#         if (self.idx + self.slider == len(self.items) - 1):
#             self.slider = 0
#             self.idx = 0
#         elif (self.idx == 3): # hold only 4 option maximum on the screen
#             self.slider += 1
#         else:
#             self.idx += 1

#     def __DrawSlider(self):
        
#         pos = int((62 / len(self.items) ) * (self.idx + self.slider)) + 1
#         nextpos = int((62 / len(self.items) ) * (self.idx + self.slider + 1)) + 1
#         if (self.idx == len(self.items) - 1):
#             nextpos = 62
#         self.draw.rectangle((125, 0, 127, 63), outline = 255, fill = None)
#         self.draw.line((126, pos, 126, nextpos), fill = 255)
#         pass
#     def __Display(self):
#         self.draw.rectangle((0,0,OLED_WIDTH, OLED_HEIGHT), fill = 0)
#         self.__DrawSlider() 
#         x = 1
#         y = 3
#         for i in range(self.slider, min(len(self.items), self.slider + 4)):
#             if i == self.slider + self.idx:
#                 self.draw.text((x,y), text = f" {self.items[i][:12]}", fill = 255, font = carousel_font) 
#                 self.draw.rounded_rectangle((x - 1, y + 1, 123, y + 13), fill = None, outline = 255, width = 1, radius = 4)
#             else:
#                 self.draw.text((x,y), text = f" {self.items[i][:12]}", fill = 255, font = carousel_font) 
            
#             y += 14
#         self.screen.DisplayImage()
#         pass

class CarouselMenu:
    def __init__(self, io : InputHandler, itemlist : dict, isBase : False):
        self.items = {}
        self.order = []
        for key, value in itemlist.items():
            if not callable(value) and type(value) == dict:
                self.items[key] = CarouselMenu(io = io, itemlist=value, isBase= False).Interactive
            else:
                self.items[key] = value
            self.order.append(key)
        self.idx = 0
        self.slider= 0 
        self.image = Image.new("1", (OLED_WIDTH, OLED_HEIGHT), color = 0)
        self.io = io
        self.draw = ImageDraw.Draw(self.image)
        self.screen = ScreenManager()
        self.isbase = isBase
        pass
    def Interactive(self):
        self.screen.InitializeSession(self.image)
        while True: 
            keypress = self.io.GetCurrentKeyPress()
            if keypress == JS_U_PIN:
                self.__Up()
            elif keypress == JS_D_PIN:
                self.__Down()
            elif keypress == BTN3_PIN:
                if not self.isbase:
                    break
            elif keypress == JS_P_PIN:
                self.items[self.order[self.idx + self.slider]]()
            self.__Display()
            time.sleep(0.05)
        self.screen.EndSession()

    def __Up(self):
        if (self.idx + self.slider == 0):
            if len(self.order) > 4:
                self.slider = len(self.order) - 4
                self.idx = 3
            else:
                self.idx = len(self.order) - 1
                self.slider = 0

        elif (self.idx == 0):
            self.slider -=1
        else:
            self.idx -= 1


    def __Down(self):
        if (self.idx + self.slider == len(self.order) - 1):
            self.slider = 0
            self.idx = 0
        elif (self.idx == 3): # hold only 4 option maximum on the screen
            self.slider += 1
        else:
            self.idx += 1

    def __DrawSlider(self):
        
        pos = int((62 / len(self.order) ) * (self.idx + self.slider)) + 1
        nextpos = int((62 / len(self.order) ) * (self.idx + self.slider + 1)) + 1
        if (self.idx == len(self.order) - 1):
            nextpos = 62
        self.draw.rectangle((125, 0, 127, 63), outline = 255, fill = None)
        self.draw.line((126, pos, 126, nextpos), fill = 255)
        pass
    def __Display(self):
        self.draw.rectangle((0,0,OLED_WIDTH, OLED_HEIGHT), fill = 0)
        self.__DrawSlider() 
        x = 1
        y = 3
        for i in range(self.slider, min(len(self.order), self.slider + 4)):
            if i == self.slider + self.idx:
                self.draw.text((x,y), text = f" {self.order[i][:12]}", fill = 255, font = carousel_font) 
                self.draw.rounded_rectangle((x - 1, y + 1, 123, y + 13), fill = None, outline = 255, width = 1, radius = 4)
            else:
                self.draw.text((x,y), text = f" {self.order[i][:12]}", fill = 255, font = carousel_font) 
            
            y += 14
        self.screen.DisplayImage()
        pass

