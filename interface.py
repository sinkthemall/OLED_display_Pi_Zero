
from iohandler import InputHandler, ScreenManager, io, screen
from config import *
from PIL import ImageDraw, Image, ImageFont
import threading

import time

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
        self.shiftkey = 0 
        self.val = None

        # index for buffer cursor
        self.curidx = 0 # current buffer index
        self.lasidx = 0 # buffer length
        self.slidefn = 0 # slide frame number

        # an control variable to track whether cursor is in buffer or in keyboard
        self.trackcursor = None
        self.image = Image.new("1", (OLED_WIDTH, OLED_HEIGHT), color=0)
        self.draw = ImageDraw.Draw(self.image)
        self.screen = ScreenManager()
        self.condition = threading.Condition()
        self.keypress = None
        self.keyboardlayout = [Image.new("1", (OLED_WIDTH, OLED_HEIGHT), color=0) for i in range(len(neokeychoice))]
        self.__PrepareKBLayout() 

    def __PrepareKBLayout(self):
        tmpdraw = [ImageDraw.Draw(self.keyboardlayout[i]) for i in range(len(self.keyboardlayout))]

        for layout in range(len(neokeychoice)):
            for i in range(KBnumrow):
                for j in range(len(neokeychoice[layout][i])):
                     tmpdraw[layout].text(( KBx_start + char_align +  j * KBx_dis, KBy_start + i * KBy_dis), text=neokeychoice[layout][i][j], fill = 255, font = KB_font, align="center")
            tmpdraw[layout].rectangle((1, 1, 126, KBy_start - 2), outline = 1, width = 1)
        pass
    def __RegisterCallback(self):
        io = InputHandler()
        io.PushInterface({ 
            JS_L_PIN : self.Left,
            JS_R_PIN : self.Right,
            JS_U_PIN : self.Up,
            JS_D_PIN : self.Down,
            JS_P_PIN : self.AdjustChar,
            BTN1_PIN : self.ConfirmOutput,
            BTN2_PIN : self.ShiftKeyboard,
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
            self.shiftkey ^= 1
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
                    if self.curidx <= self.slidefn and self.slidefn > 0:
                        self.slidefn -= 1
            elif self.keypress == JS_R_PIN:
                if self.curidx < self.lasidx:
                    self.curidx += 1
                    if self.slidefn + SLIDE_SIZE == self.curidx:
                        self.slidefn += 1
            elif self.keypress == JS_P_PIN:
                # in buffer cursor, it become delete button, but in keyboard cursor, it become add button
                if self.curidx > 0:
                    for i in range(self.curidx, self.lasidx):
                        self.buffer[i - 1] = self.buffer[i]
                    self.lasidx -= 1
                    self.curidx -= 1
                    if self.slidefn > 0:
                        self.slidefn -= 1 
            return 
        elif self.trackcursor == 1: # in keyboard
            if self.keypress == JS_U_PIN:
                if self.idx_I == 0:
                    self.trackcursor = 0
                else:
                    self.idx_I -= 1
                
            elif self.keypress == JS_D_PIN :
                if self.idx_I + 1 < KBnumrow:
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
                self.buffer[self.curidx] = neokeychoice[self.shiftkey][self.idx_I][min(len(neokeychoice[self.shiftkey][self.idx_I]) - 1, self.idx_J)] # this allow to remember the last key in case of space moving to adjacent key
                self.curidx += 1
                self.lasidx += 1
                if self.slidefn + SLIDE_SIZE <= self.curidx:
                    self.slidefn += 1

            pass

    def GetVal(self):
        return self.val

    def Interactive(self, prompt=""):
        # io = InputHandler()
        self.__RegisterCallback()
        self.trackcursor = 0
        self.shiftkey = 0
        self.idx_I = 0
        self.idx_J = 0
        self.val = None
        self.slidefn = 0
        self.curidx = 0
        self.lasidx = 0
        self.screen.InitializeSession(self.image)

        while True:
            # self.__Display() # in case of keyboard, there are too many calls to drawing, which can slow
            # process, so we use a method call LazyDrawing (I made that name), which only draw to the actual changing
            # cursor, not the whole keyboard
            self.__LazyDraw()
            with self.condition:
                self.condition.wait()
            if self.keypress == BTN3_PIN or self.keypress == BTN1_PIN:
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
        if self.lasidx <= 0:
            self.val = ""
        else:
            self.val = "".join(self.buffer[i] for i in range(self.lasidx))
        print(f"value : {self.val}")
        self.keypress = BTN1_PIN
        with self.condition :
            self.condition.notify()

    def ShiftKeyboard(self): 

        self.keypress = BTN2_PIN
        with self.condition:
            self.condition.notify()


    def AdjustChar(self):

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

    def __LazyDraw(self):
        '''
        Paste whole keyboard, not draw characters one by one
        '''
        # LazyReDraw work by copy-paste the no-cursor region. There are n-image (include all the shift keyboard) of keyboard with no cursor
        # And it work by just copying the keyboard into our current image.
        # In my original solution, I only want to redraw the affect cursor.
        # but since my new method also call the draw (or Image.pase()) only once
        # even with a larger region, it is not really a problem in performance (Image handling bit image in byte, bitset), therefore I chose to paste region instead of redoing the draw cursor process (which take more
        # code to handle)
        # With buffer and cursor, I draw each by calling draw function
        self.image.paste(self.keyboardlayout[self.shiftkey], (0, 0, 128, 64))
        if self.trackcursor == 0: 
            self.draw.rectangle((0, 0, 127, KBy_start - 1), outline = 255, width = 1)
        elif self.trackcursor  == 1:
            if (self.idx_I == KBnumrow - 1) and (self.idx_J >= len(neokeychoice[self.shiftkey][KBnumrow - 1]) - 1):
                self.draw.rounded_rectangle((KBx_start + (KBlastnumcol - 1)* KBx_dis, KBy_start + self.idx_I * KBy_dis, KBx_start + KBnumcol * KBx_dis, KBy_start + KBnumrow * KBy_dis ), outline = 255, width = 1, radius = 2)
            else:
                self.draw.rounded_rectangle((KBx_start +  self.idx_J * KBx_dis, KBy_start + self.idx_I * KBy_dis,KBx_start + (self.idx_J + 1) * KBx_dis, KBy_start + (self.idx_I + 1) * KBy_dis), outline = 255, width = 1, radius = 2)
        for i in range(self.slidefn, min(self.slidefn + SLIDE_SIZE, self.lasidx)):
            self.draw.text(( KBbuf_start +  KBchar_dis * (i - self.slidefn) + 2, 2), text = self.buffer[i], font = KBbuf_font, fill = 255)
        

        # self.draw.text(( 4 +  KBchar_dis * (i - self.slidefn) + 2, 2), text= "󱞪", fill = 255, font = KBbuf_font)
        self.draw.line((KBbuf_start + KBchar_dis * (self.curidx - self.slidefn) + 2, 13, KBbuf_start + KBchar_dis * (self.curidx - self.slidefn) + 2 + KBcursor_len, 13 ), fill = 255, width=1)
        
        self.screen.DisplayImage()

keyboard = NeoKeyboard()
# neokeyboard = NeoKeyboard()

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
        self.prompt = None
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

    def Interactive(self):
        self.__RegisterCallback()

        self.slider = 0
        self.idx = 0
        self.screen.InitializeSession(self.image)
        # print("[+] Init image done")
        val = None

        while True:
            self.__Display(self.prompt)
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
    def LoadItems(self, items, prompt = ""):
        self.items = items
        self.prompt = prompt

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

        while True: 
            self.__Display()
            with self.condition:
                self.condition.wait()

            if self.keypress == JS_P_PIN:
                self.items[self.idx + self.slider]()
            elif self.keypress == BTN3_PIN:
                if not self.isbase:
                    break
            # self.keypress = None

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

    