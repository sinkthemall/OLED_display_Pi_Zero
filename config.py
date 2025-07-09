from PIL import ImageFont

# config.py
OLED_WIDTH = 128
OLED_HEIGHT = 64

# SPI or I2C Selection
USE_SPI = True  # Set to False for I2C, currently I2C is unsupported

# GPIO Pin Definitions
RST_PIN = 25
DC_PIN = 24
CS_PIN = 8

# Joystick and Buttons
JS_U_PIN = 6
JS_D_PIN = 19
JS_L_PIN = 5
JS_R_PIN = 26
JS_P_PIN = 13
BTN1_PIN = 21
BTN2_PIN = 20
BTN3_PIN = 16



# NeoKeyboard config
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
KBnumrow = 5
KBnumcol = 10
KBx_start = 4
KBy_start = 13 + 5 # where first row to be draw
KBy_dis = (63 - KBy_start) // KBnumrow
KBx_dis = 120 // KBnumcol
char_align = 4
KBlastnumcol = 8
KB_font = ImageFont.truetype("UbuntuMono-R.ttf", size = 9)
KBbuf_font = ImageFont.truetype("UbuntuMono-R.ttf", size = 11)
KBchar_dis = 8
KBbuf_start = 8
KBcursor_len = 4

# Idk config, will sorting it later
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
prompt_item_font = ImageFont.truetype("DejaVuSans-Bold.ttf", size = 10)
SLIDE_SIZE = 14
# projector_font = ImageFont.truetype("Hack-Regular.ttf", size = 11)
projector_font = ImageFont.truetype("DejaVuSans.ttf", size = 11)
