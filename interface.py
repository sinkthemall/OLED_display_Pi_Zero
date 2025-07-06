
from iohandler import InputHandler, ScreenManager, io, screen
from config import *
from PIL import ImageDraw, Image, ImageFont
import threading

import time
keychoice = [
	["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"],
	["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"],
	["0","1","2","3","4","5","6","7","8","9","+","-","*","/","&","|","^","~","(",")","[","]","{","}","<",">"],
    ["!","@","#","$","%","_","=",";",":","'",'"',",",".","?","`","\\",]
]

neokeychoice = [[
        ['1', '2', '3', '4' ,'5', '6', '7', '8', '9', '0'],
        ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'], 
        ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';'],
        ['z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', "'"], 
        ['-', '=', '[', ']', '/', '`', '\\', ' ']
    ], [
        ['!', '@', '#', '$' ,'%', '^', '&', '*', '(', ')'],
        ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'], 
        ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ':'],
        ['Z', 'X', 'C', 'V', 'B', 'N', 'M', '<', '>', '"'], 
        ['_', '+', '{', '}', '?', '~', '|',  ' '],
    ]]
numrow = 5

font = ImageFont.truetype("UbuntuMono-B.ttf", size=14)
titlefont = ImageFont.truetype("UbuntuMono-R.ttf", size = 12)
# carousel_font = ImageFont.truetype("Roboto-Medium.ttf", size = 11)
carousel_font = ImageFont.truetype("DejaVuSansMono-Bold.ttf", size = 11)

item_font = ImageFont.truetype("DejaVuSans.ttf", size = 10)
prompt_item_font = ImageFont.truetype("DejaVuSans-Bold.ttf", size = 10)
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
        self.condition = threading.Condition()

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
    
    def Return(self):
        with self.condition:
            self.condition.notify()

    def Register(self, waitforkey):
        io = InputHandler()
        if waitforkey:
            io.PushInterface({
                JS_D_PIN : self.Return ,
                JS_U_PIN : self.Return ,
                JS_L_PIN : self.Return , 
                JS_R_PIN : self.Return ,
                JS_P_PIN : self.Return ,
                BTN3_PIN : self.Return ,
            })
        else:
            io.PushInterface({})

    def Unregister(self):
        io  =InputHandler()
        io.PopInterface()

    def Display(self, waitforkey=False, timedisplay=3):
        self.Register(waitforkey=waitforkey)
        self.screen.InitializeSession(self.image)
        self.screen.DisplayImage()
        if waitforkey:
            with self.condition:
                self.condition.wait()
        else:
            time.sleep(timedisplay)

        self.screen.EndSession()
        self.Unregister()
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
        self.condition = threading.Condition()
        self.keypress=  None
        # self.RegisterCallback()

    def __RegisterCallback(self):
        io = InputHandler()
        io.PushInterface({
            JS_L_PIN : self.Left,
            JS_R_PIN : self.Right,
            JS_U_PIN : self.Up,
            JS_D_PIN : self.Down,
            JS_P_PIN : self.AddChar,
            BTN1_PIN : self.DelChar,
            BTN2_PIN : self.ConfirmOutput,
            BTN3_PIN : self.Back
        })
        # pass

    def __UnregisterCallback(self):
        io = InputHandler()
        io.PopInterface()

    def GetVal(self):
        return self.val

    def Interactive(self, prompt=""):
        # io = InputHandler()
        self.__RegisterCallback()

        self.index = 0
        self.buffer[0] = (0, 0)
        self.val = None
        self.prompt = prompt[:20] + ".." if len(prompt) > 20 else prompt
        self.screen.InitializeSession(self.image)

        while True:
            self.__Display()
            with self.condition:
                self.condition.wait()
            if self.keypress == BTN3_PIN or self.keypress == BTN2_PIN:
                break
                # if self.keypress == JS_L_PIN:
                #     self.Left()
                # elif self.keypress == JS_R_PIN:
                #     self.Right()
                # elif self.keypress == JS_U_PIN:
                #     self.Up()
                # elif self.keypress == JS_D_PIN:
                #     self.Down()
                # elif self.keypress == BTN1_PIN:
                #     self.DelChar()
                # elif self.keypress == JS_P_PIN:
                #     self.AddChar()
                # elif self.keypress == BTN3_PIN:  # Cancel input
                #     break
                # elif self.keypress == BTN2_PIN:  # Confirm input
                    
                #     break
                # time.sleep(0.05)
                

        self.screen.EndSession()
        # if moving RegisterCallback() and UnregisterCallback() into ctor/dtor
        # then instance with singleton pattern will never call UnregisterCallback()
        # Find a way to fix thjs, instead of putting in Interactive()
        self.__UnregisterCallback() 

    def Back(self):
        self.val = None
        self.keypress = BTN3_PIN
        with self.condition:
            self.condition.notify()
    
    def ConfirmOutput(self):
        self.val = "".join(keychoice[x][y]  for x, y in self.buffer[:self.index + 1])
        self.keypress = BTN2_PIN
        with self.condition :
            self.condition.notify()

    def DelChar(self):
        self.index = max(0, self.index - 1)
        self.keypress = BTN1_PIN
        with self.condition:
            self.condition.notify()


    def AddChar(self):
        if self.index < 127:  # Prevent buffer overflow
            self.index += 1
            self.buffer[self.index] = (0, 0)
        self.keypress = JS_P_PIN
        with self.condition:
            self.condition.notify()

    def Up(self):
        x, y = self.buffer[self.index]
        if x > 0:
            self.buffer[self.index] = (x - 1, y)
        self.keypress = JS_U_PIN
        with self.condition:
            self.condition.notify()

    def Down(self):
        x, y = self.buffer[self.index]
        if x < 3 and y < len(keychoice[x + 1]):
            self.buffer[self.index] = (x + 1, y)
        self.keypress = JS_D_PIN
        with self.condition:
            self.condition.notify()

    def Left(self):
        x, y = self.buffer[self.index]
        self.buffer[self.index] = (x, (y - 1) % len(keychoice[x]))
        self.keypress = JS_L_PIN
        with self.condition:
            self.condition.notify()


    def Right(self):
        x, y = self.buffer[self.index]
        self.buffer[self.index] = (x, (y + 1) % len(keychoice[x]))  # Fixed from (y - 1) to (y + 1)
        self.keypress = JS_R_PIN
        with self.condition:
            self.condition.notify()

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

class NeoKeyboard :
    _instance = None  # Singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NeoKeyboard, cls).__new__(cls)
            cls._instance.__initialize()  # Call a private initializer method
        return cls._instance

    def __initialize(self):
        """
        Private initialization method to prevent re-initialization.
        """
        self.buffer = [None for i in range(128)]  # Limit input to 127 characters
        # index for current keyboard cursor
        self.idx_I = None
        self.idx_J = None
        self.shiftkey = None 
        self.val = None

        # index for buffer cursor
        self.curidx = 0
        self.lasidx = 0

        # an control variable to track whether cursor is in buffer or in keyboard
        self.trackcursor = None

        self.draw = ImageDraw.Draw(Image.new("1", (OLED_WIDTH, OLED_HEIGHT), color=0))
        self.screen = ScreenManager()
        self.condition = threading.Condition()
        self.keypress = None

    def __RegisterCallback(self):
        io = InputHandler()
        io.PushInterface({ 
            JS_L_PIN : self.Left,
            JS_R_PIN : self.Right,
            JS_U_PIN : self.Up,
            JS_D_PIN : self.Down,
            JS_P_PIN : self.AddChar,
            BTN1_PIN : self.DelChar,
            BTN2_PIN : self.ConfirmOutput,
            BTN3_PIN : self.Back
        })
        # pass

    def __UnregisterCallback(self):
        io = InputHandler()
        io.PopInterface()

    def __KeyHandling(self):
        # Confirm input
        if self.keypress == BTN1_PIN:
            
            return 
        elif self.keypress == BTN3_PIN: # back button
            return
        # Shift keyboard:
        elif self.keypress == BTN2_PIN:
            self.shiftkey += 1
            self.shiftkey %= len(neokeychoice)
            return 
        
        if self.trackcursor == 0: # in buffer
            if self.keypress == JS_U_PIN:
                pass
            elif self.keypress == JS_D_PIN:
                self.trackcursor = 1

            # Moving cursor to next/prev character
            elif self.keypress == JS_L_PIN:
                if self.curidx > 0 :
                    self.curidx -=1
            elif self.keypress == JS_R_PIN:
                if self.curidx <= self.lasidx:
                    self.curidx += 1
            elif self.keypress == JS_P_PIN:
                # in buffer cursor, it become delete button, but in keyboard cursor, it become add button
                if self.lasidx >0 :
                    for i in range(self.curidx, self.lasidx):
                        self.buffer[i] = self.buffer[i + 1]
                    self.lasidx -= 1
                    if self.curidx > self.lasidx:
                        self.curidx = self.lasidx
            return 
            
        elif self.trackcursor == 1: # in keyboard
            if self.keypress == JS_U_PIN:
                if self.idx_I == 0:
                    self.trackcursor == 0
                else:
                    self.idx_I -= 1
                
            elif self.keypress == JS_D_PIN :
                if self.idx_I + 1 < numrow:
                    self.idx_I += 1
                
            elif self.keypress == JS_L_PIN:
                self.idx_J = min(len(neokeychoice[self.shiftkey][self.idx_I]) - 1, self.idx_J)
                self.idx_J -= 1
                self.idx_J %= len(neokeychoice[self.shiftkey][self.idx_I])
                
            elif self.keypress == JS_R_PIN:
                self.idx_J = min(len(neokeychoice[self.shiftkey][self.idx_I]) - 1, self.idx_J)
                self.idx_J += 1
                self.idx_J %= len(neokeychoice[self.shiftkey][self.idx_I])
            elif self.keypress == JS_P_PIN:
                if (self.lasidx == 127) :
                    return 
                
                for i in range(self.lasidx - 1, self.curidx - 1, -1):
                    self.buffer[i + 1] = self.buffer[i]
                self.buffer[self.curidx] = neokeychoice[self.shiftkey][self.idx_I][min(len(neokeychoice[self.shiftkey][self.idx_I]) - 1, self.idx_J)]
                if self.curidx == self.lasidx:
                    self.curidx += 1
                self.lasidx += 1
            pass

    def GetVal(self):
        return self.val

    def Interactive(self, prompt=""):
        # io = InputHandler()
        self.__RegisterCallback()
        self.trackcursor = 0
        self.screen.InitializeSession(self.image)

        while True:
            # self.__Display() # in case of keyboard, there are too many calls to drawing, which can slow
            # process, so we use a method call LazyDrawing (I made that name), which only draw to the actual changing
            # cursor, not the whole keyboard
            with self.condition:
                self.condition.wait()
            if self.keypress == BTN3_PIN or self.keypress == BTN2_PIN:
                break
            self.__KeyHandling()
            if self.val != None:
                break

        self.screen.EndSession()
        # if moving RegisterCallback() and UnregisterCallback() into ctor/dtor
        # then instance with singleton pattern will never call UnregisterCallback()
        # Find a way to fix thjs, instead of putting in Interactive()
        self.__UnregisterCallback() 

    def Back(self):
        self.val = None
        self.keypress = BTN3_PIN
        with self.condition:
            self.condition.notify()
    
    def ConfirmOutput(self):
        if self.lasidx < 0:
            self.val = ""
        else:
            self.val = "".join(self.buffer[i] for i in range(self.lasidx))
        self.keypress = BTN2_PIN
        with self.condition :
            self.condition.notify()

    def DelChar(self):

        self.keypress = BTN1_PIN
        with self.condition:
            self.condition.notify()


    def AddChar(self):

        self.keypress = JS_P_PIN
        with self.condition:
            self.condition.notify()

    def Up(self):
        self.keypress = JS_U_PIN
        with self.condition:
            self.condition.notify()

    def Down(self):
        self.keypress = JS_D_PIN
        with self.condition:
            self.condition.notify()

    def Left(self):
        self.keypress = JS_L_PIN
        with self.condition:
            self.condition.notify()


    def Right(self):

        self.keypress = JS_R_PIN
        with self.condition:
            self.condition.notify()

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

    def __LazyReDraw(self):
        '''
        Clear the cursor, not redraw entire keyboard
        '''
        # LazyReDraw work by copy-paste the no-cursor region. There are n-image (include all the shift keyboard) of keyboard with no cursor
        # And it work by just copying the keyboard into our current image.
        # In my original solution, I only want to redraw the affect cursor.
        # but since my new method also call the draw (or Image.pase()) only once
        # even with a larger region, it is not really a problem in performance (Image handling bit image in byte, bitset), therefore I chose to paste region instead of redoing the draw cursor process (which take more
        # code to handle)
        pass
    def __LazyDraw(self):
        '''
        Draw the cursor, not redraw entire keyboard
        '''

        pass

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
        self.items = None
        self.image = Image.new("1", (OLED_WIDTH, OLED_HEIGHT), color=0)
        self.draw = ImageDraw.Draw(self.image)
        self.slider = 0
        self.idx = 0
        self.screen = ScreenManager()
        self.condition = threading.Condition()
        self.keypress = None

    def __RegisterCallback(self):
        io = InputHandler()
        io.PushInterface({
            JS_U_PIN : self.Up,
            JS_D_PIN : self.Down,
            JS_P_PIN : self.Enter,
            BTN3_PIN : self.Back
        })
        pass

    def __UnregisterCallback(self):
        io = InputHandler()
        io.PopInterface()
        pass

    def Interactive(self, items, prompt=""):
        self.items = items
        self.__RegisterCallback()

        self.slider = 0
        self.idx = 0
        self.screen.InitializeSession(self.image)
        # print("[+] Init image done")
        val = None

        while True:
            self.__Display(prompt)
            with self.condition:
                self.condition.wait()
            if self.keypress == BTN3_PIN:
                break
            elif self.keypress == JS_P_PIN:
                val = self.slider + self.idx
                break
            self.keypress = None

        self.screen.EndSession()
        self.__UnregisterCallback()
        self.items = None
        return val

    def Back(self):
        self.keypress = BTN3_PIN
        with self.condition:
            self.condition.notify()
    
    def Enter(self):
        self.keypress = JS_P_PIN
        with self.condition:
            self.condition.notify()

    def Up(self):
        """
        Handles moving the selection up.
        """
        if (len(self.items) != 0):
            if (self.idx | self.slider) == 0:
                if len(self.items) > 4:
                    self.slider = len(self.items) - 4
                    self.idx = 3
                else:
                    self.idx = len(self.items) - 1
                    self.slider = 0
            elif self.idx == 0:
                self.slider -= 1
            else:
                self.idx -= 1
        self.keypress = JS_U_PIN
        with self.condition:
            self.condition.notify()

    def Down(self):
        """
        Handles moving the selection down.
        """
        if len(self.items) != 0:
            if self.idx + self.slider == len(self.items) - 1:
                self.slider = 0
                self.idx = 0
            elif self.idx == 3:  # Max options visible on screen: 4
                self.slider += 1
            else:
                self.idx += 1
        self.keypress = JS_D_PIN
        with self.condition:
            self.condition.notify()

        
    # def __YesnoDisplay(self, items, prompt):
    #     self.draw.rectangle((0, 0, OLED_WIDTH, OLED_HEIGHT), fill=0)
    #     self.draw.text((1, 1), text= prompt, fill = 255, font = titlefont)
    #     self.draw.text((20, 3 + 11 * 3), text = items[0], fill = 255, font = item_font)
    #     self.draw.text((20, 3 + 11 * 4), text = items[1], fill = 255, font = item_font)
    #     self.draw.text((1, 3 + 11 * (3 + self.idx)), text = ">", fill = 255, font = item_font)
    #     self.screen.DisplayImage()
    def __Display(self, prompt : str):
        """
        Handles drawing the list on the screen.
        """
        self.draw.rectangle((0, 0, OLED_WIDTH, OLED_HEIGHT), fill=0)
        self.draw.text((1, 1), text= prompt.upper(), fill = 255, font = prompt_item_font)
        self.draw.line((0, 12, 127, 12), width = 1, fill = 255)

        if len(self.items) != 0:

            x, y = 1, 13

            for i in range(self.slider, min(len(self.items), self.slider + 4)):
                self.draw.text((x + 10, y), text=f"{self.items[i][:20]}", fill=255, font=item_font)
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
        self.keypress = None
        self.idx = 0
        self.slider= 0 
        self.image = Image.new("1", (OLED_WIDTH, OLED_HEIGHT), color = 0)
        self.draw = ImageDraw.Draw(self.image)
        self.isbase = isBase
        self.screen = ScreenManager()
        self.condition = threading.Condition()


        pass
    def __RegisterCallback(self):
        io = InputHandler()
        io.PushInterface({
            JS_U_PIN : self.Up,
            JS_D_PIN : self.Down,
            JS_P_PIN : self.Enter,
            BTN3_PIN : self.Back
        })
    
    def __UnregisterCallback(self):
        io = InputHandler()
        io.PopInterface()

    def Interactive(self):
        self.__RegisterCallback()
        self.screen.InitializeSession(self.image)
        # io = InputHandler()
        # while True: 
        #     with self.condition:
        #     self.__Display()
        #     keypress = io.GetCurrentKeyPress()
        #     if keypress == JS_U_PIN:
        #         self.Up()
        #     elif keypress == JS_D_PIN:
        #         self.__Down()
        #     elif keypress == BTN3_PIN:
        #         if not self.isbase:
        #             break
        #     elif keypress == JS_P_PIN:
        #         self.items[self.idx + self.slider]()
            
        #     time.sleep(0.05)

        while True: 
            self.__Display()
            with self.condition:
                self.condition.wait()

            if self.keypress == JS_P_PIN:
                self.items[self.idx + self.slider]()
            elif self.keypress == BTN3_PIN:
                if not self.isbase:
                    break

            self.keypress = None

        self.screen.EndSession()
        self.__UnregisterCallback()

    def Enter(self):
        self.keypress = JS_P_PIN
        with self.condition:
            self.condition.notify()
    
    def Back(self):
        self.keypress = BTN3_PIN
        with self.condition:
            self.condition.notify()

    def Up(self):
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

        self.keypress = JS_U_PIN
        with self.condition:
            self.condition.notify()

    def Down(self):
        if (self.idx + self.slider == len(self.labels) - 1):
            self.slider = 0
            self.idx = 0
        elif (self.idx == 3): # hold only 4 option maximum on the screen
            self.slider += 1
        else:
            self.idx += 1

        self.keypress = JS_D_PIN
        with self.condition:
            self.condition.notify()

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

    