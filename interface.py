
from iohandler import InputHandler, ScreenManager, io, screen
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
# carousel_font = ImageFont.truetype("Roboto-Medium.ttf", size = 11)
carousel_font = ImageFont.truetype("DejaVuSansMono-Bold.ttf", size = 11)

item_font = ImageFont.truetype("DejaVuSans.ttf", size = 10)
SLIDE_SIZE = 14
# projector_font = ImageFont.truetype("Hack-Regular.ttf", size = 11)
projector_font = ImageFont.truetype("DejaVuSans.ttf", size = 11)
class Projector:
    _instance = None  # Singleton instance

    def __new__(cls, io=io):
        if cls._instance is None:
            cls._instance = super(Projector, cls).__new__(cls)
            cls._instance._initialized = False  # Ensure __init__ runs only once
        return cls._instance

    def __init__(self, io=io):
        if self._initialized:
            return  # Prevent re-initialization in case of multiple calls

        self.io = io
        self.screen = screen
        self.image = Image.new("1", (OLED_WIDTH, OLED_HEIGHT), color=0)
        self.draw = ImageDraw.Draw(self.image)
        self._initialized = True  # Mark as initialized

    def DrawText(self, coor, text, font=projector_font):
        # it does not auto fit
        self.draw.text(coor, text = text, font = font, fill = 255)
        pass
    
    def CenterText(self, y , text, font = projector_font):
        bbox = self.draw.textbbox((0,0), text = text, font=font)
        text_width = bbox[2] - bbox[0]
        # text_height = bbox[3] - bbox[1]
        x = (OLED_WIDTH - text_width)//2
        self.draw.text((x, y), text= text, font= font, fill= 255)
    


    def Display(self, waitforkey=False, timedisplay=3):
        self.screen.InitializeSession(self.image)
        self.screen.DisplayImage()
        if waitforkey:
            while True:
                keypress = self.io.GetCurrentKeyPress()
                if keypress is not None:
                    break
        else:
            time.sleep(timedisplay)

        self.screen.EndSession()

    def Reset(self):
        self.draw.rectangle((0, 0, OLED_WIDTH, OLED_HEIGHT), fill=0)

    def DrawImage(self, path, scale):
        self.Reset()
        original_image = Image.open(path).convert("1")
        scale_factor = scale
        scaled_width = int(original_image.width * scale_factor)
        scaled_height = int(original_image.height * scale_factor)
        scaled_image = original_image.resize((scaled_width, scaled_height), Image.Resampling.LANCZOS)

        oled_width, oled_height = 128, 64
        x_offset = (oled_width - scaled_width) // 2
        y_offset = (oled_height - scaled_height) // 2
        self.image.paste(scaled_image, (x_offset, y_offset))
        
projector = Projector()


class KeyBoard:
    _instance = None  # Singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(KeyBoard, cls).__new__(cls)
            cls._instance.__initialize()  # Call a private initializer method
        return cls._instance

    def __initialize(self):
        """
        Private initialization method to prevent re-initialization.
        """
        self.buffer = [(0, 0) for _ in range(128)]  # Limit input to 128 characters
        self.index = 0
        self.prompt = ""
        self.val = None
        self.image = Image.new("1", (OLED_WIDTH, OLED_HEIGHT), color=0)
        self.draw = ImageDraw.Draw(self.image)
        self.screen = ScreenManager()

    def GetVal(self):
        return self.val

    def Interactive(self, prompt=""):
        io = InputHandler()
        self.index = 0
        self.buffer[0] = (0, 0)
        self.val = None
        self.prompt = prompt[:20] + ".." if len(prompt) > 20 else prompt
        self.screen.InitializeSession(self.image)

        while True:
            self.__Display()
            keypress = io.GetCurrentKeyPress()
            if keypress == JS_L_PIN:
                self.__Left()
            elif keypress == JS_R_PIN:
                self.__Right()
            elif keypress == JS_U_PIN:
                self.__Up()
            elif keypress == JS_D_PIN:
                self.__Down()
            elif keypress == BTN1_PIN:
                self.__DelChar()
            elif keypress == JS_P_PIN:
                self.__AddChar()
            elif keypress == BTN3_PIN:  # Cancel input
                self.val = None
                break
            elif keypress == BTN2_PIN:  # Confirm input
                self.val = "".join(keychoice[x][y]  for x, y in self.buffer[:self.index + 1])
                break
            # time.sleep(0.05)
            

        self.screen.EndSession()

    def __DelChar(self):
        self.index = max(0, self.index - 1)

    def __AddChar(self):
        if self.index < 127:  # Prevent buffer overflow
            self.index += 1
            self.buffer[self.index] = (0, 0)

    def __Up(self):
        x, y = self.buffer[self.index]
        if x > 0:
            self.buffer[self.index] = (x - 1, y)

    def __Down(self):
        x, y = self.buffer[self.index]
        if x < 3 and y < len(keychoice[x + 1]):
            self.buffer[self.index] = (x + 1, y)

    def __Left(self):
        x, y = self.buffer[self.index]
        self.buffer[self.index] = (x, (y - 1) % len(keychoice[x]))

    def __Right(self):
        x, y = self.buffer[self.index]
        self.buffer[self.index] = (x, (y + 1) % len(keychoice[x]))  # Fixed from (y - 1) to (y + 1)

    def __Display(self):
        x, y = 1, 26
        self.draw.rectangle((0, 0, OLED_WIDTH, OLED_HEIGHT), fill=0)
        self.draw.text((1, 1), text=self.prompt, fill=255, font=titlefont)
        
        st = max(0, self.index - SLIDE_SIZE + 1) if self.index >= SLIDE_SIZE - 1 else 0
        for i in range(st, self.index + 1):
            keyx, keyy = self.buffer[i]
            self.draw.text((x, y), text=keychoice[keyx][keyy], fill=255, font=font)
            x += 9

        self.draw.text((x - 9, y + 3), text="_", fill=255, font=font)
        self.screen.DisplayImage()

keyboard = KeyBoard()


class ListOption: 
    # an exact copy cat of carousel menu, but item list is flexible, not storing and only return value
    # for now, it will display as same as carousel, with no slider, but I will fix it later
    # why need to complicate it :)))
    _instance = None  # Singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ListOption, cls).__new__(cls)
            cls._instance.__initialize()  # Call a private initializer method
        return cls._instance

    def __initialize(self):
        """
        Private initialization method to prevent re-initialization.
        """
        self.image = Image.new("1", (OLED_WIDTH, OLED_HEIGHT), color=0)
        self.draw = ImageDraw.Draw(self.image)
        self.slider = 0
        self.idx = 0
        self.screen = ScreenManager()

    def Interactive(self, items, prompt="", yesno=False):
        self.slider = 0
        self.idx = 0
        self.screen.InitializeSession(self.image)
        # print("[+] Init image done")
        val = None
        io = InputHandler()
        if yesno:
            while True:
                self.__YesnoDisplay(items, prompt=prompt)
                keypress = io.GetCurrentKeyPress()
                if keypress == JS_U_PIN or keypress == JS_D_PIN:
                    self.idx ^= 1
                elif keypress == BTN3_PIN:  # Exit option
                    break
                elif keypress == JS_P_PIN:  # Select option
                    val = self.idx
                    break
                
                time.sleep(0.05)

            pass  # Placeholder for Yes/No handling
        else:
            while True:
                self.__Display(items)
                keypress = io.GetCurrentKeyPress()
                if keypress == JS_U_PIN:
                    self.__Up(items)
                elif keypress == JS_D_PIN:
                    self.__Down(items)
                elif keypress == BTN3_PIN:  # Exit option
                    break
                elif keypress == JS_P_PIN:  # Select option
                    val = self.slider + self.idx
                    break
                
                time.sleep(0.05)

        self.screen.EndSession()
        return val

    def __Up(self, items):
        """
        Handles moving the selection up.
        """
        if (len(items) != 0):
            if self.idx + self.slider == 0:
                if len(items) > 5:
                    self.slider = len(items) - 5
                    self.idx = 4
                else:
                    self.idx = len(items) - 1
                    self.slider = 0
            elif self.idx == 0:
                self.slider -= 1
            else:
                self.idx -= 1

    def __Down(self, items):
        """
        Handles moving the selection down.
        """
        if len(items) != 0:
            if self.idx + self.slider == len(items) - 1:
                self.slider = 0
                self.idx = 0
            elif self.idx == 4:  # Max options visible on screen: 5
                self.slider += 1
            else:
                self.idx += 1
    def __YesnoDisplay(self, items, prompt):
        self.draw.rectangle((0, 0, OLED_WIDTH, OLED_HEIGHT), fill=0)
        self.draw.text((1, 1), text= prompt, fill = 255, font = titlefont)
        self.draw.text((20, 3 + 11 * 3), text = items[0], fill = 255, font = item_font)
        self.draw.text((20, 3 + 11 * 4), text = items[1], fill = 255, font = item_font)
        self.draw.text((1, 3 + 11 * (3 + self.idx)), text = ">", fill = 255, font = item_font)
        self.screen.DisplayImage()
    def __Display(self, items):
        """
        Handles drawing the list on the screen.
        """
        self.draw.rectangle((0, 0, OLED_WIDTH, OLED_HEIGHT), fill=0)
        if len(items) != 0:

            x, y = 1, 3

            for i in range(self.slider, min(len(items), self.slider + 5)):
                self.draw.text((x + 10, y), text=f"{items[i][:20]}", fill=255, font=item_font)
                if i == self.slider + self.idx:
                    self.draw.text((x, y), text=f">", fill=255, font=item_font)
                y += 11

        # print("[+] Image display")
        self.screen.DisplayImage()

class RangeAdjust:
    def __init__(self):
        pass



class CarouselMenu:
    def __init__(self, itemlist : dict, isBase : False):
        self.items = []
        self.labels = []
        for key, value in itemlist.items():
            self.items.append(value)
            self.labels.append(key)
        self.idx = 0
        self.slider= 0 
        self.image = Image.new("1", (OLED_WIDTH, OLED_HEIGHT), color = 0)
        self.draw = ImageDraw.Draw(self.image)
        self.isbase = isBase
        self.screen = ScreenManager()
        pass
    def Interactive(self):
        self.screen.InitializeSession(self.image)
        io = InputHandler()
        while True: 
            self.__Display()
            keypress = io.GetCurrentKeyPress()
            if keypress == JS_U_PIN:
                self.__Up()
            elif keypress == JS_D_PIN:
                self.__Down()
            elif keypress == BTN3_PIN:
                if not self.isbase:
                    break
            elif keypress == JS_P_PIN:
                self.items[self.idx + self.slider]()
            
            time.sleep(0.05)
        self.screen.EndSession()

    def __Up(self):
        if (self.idx + self.slider == 0):
            if len(self.labels) > 4:
                self.slider = len(self.labels) - 4
                self.idx = 3
            else:
                self.idx = len(self.labels) - 1
                self.slider = 0

        elif (self.idx == 0):
            self.slider -=1
        else:
            self.idx -= 1


    def __Down(self):
        if (self.idx + self.slider == len(self.labels) - 1):
            self.slider = 0
            self.idx = 0
        elif (self.idx == 3): # hold only 4 option maximum on the screen
            self.slider += 1
        else:
            self.idx += 1

    def __DrawSlider(self):
        
        pos = int((62 / len(self.labels) ) * (self.idx + self.slider)) + 1
        nextpos = int((62 / len(self.labels) ) * (self.idx + self.slider + 1)) + 1
        if (self.idx == len(self.labels) - 1):
            nextpos = 62
        self.draw.rectangle((125, 0, 127, 63), outline = 255, fill = None)
        self.draw.line((126, pos, 126, nextpos), fill = 255)
        pass
    def __Display(self):
        self.draw.rectangle((0,0,OLED_WIDTH, OLED_HEIGHT), fill = 0)
        self.__DrawSlider() 
        x = 1
        y = 3
        for i in range(self.slider, min(len(self.labels), self.slider + 4)):
            if i == self.slider + self.idx:
                self.draw.text((x,y), text = f" {self.labels[i][:20]}", fill = 255, font = carousel_font) 
                self.draw.rounded_rectangle((x - 1, y + 1, 123, y + 13), fill = None, outline = 255, width = 1, radius = 4)
            else:
                self.draw.text((x,y), text = f" {self.labels[i][:20]}", fill = 255, font = carousel_font) 
            
            y += 14
        self.screen.DisplayImage()
        pass

