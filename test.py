# import RPi.GPIO as GPIO
# import time
# import config  # Import your config file with pin definitions

# class InputHandler:
#     def __init__(self, callback_function=None):
#         """
#         Initializes the GPIO buttons & joystick and sets up event detection.
#         :param callback_function: Function to call when a key is pressed
#         """
#         self.callback = callback_function  # Function to call on key press

#         # Set GPIO mode
#         GPIO.setmode(GPIO.BCM)

#         # List of input pins (Joystick + Buttons)
#         self.input_pins = {
#             "UP": config.JS_U_PIN,
#             "DOWN": config.JS_D_PIN,
#             "LEFT": config.JS_L_PIN,
#             "RIGHT": config.JS_R_PIN,
#             "PRESS": config.JS_P_PIN,
#             "BTN1": config.BTN1_PIN,
#             "BTN2": config.BTN2_PIN,
#             "BTN3": config.BTN3_PIN,
#         }

#         # Setup GPIO pins as input with pull-up resistors
#         for key, pin in self.input_pins.items():
#             GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#         # Register event listeners
#         self.register_callbacks()

#     def register_callbacks(self):
#         """Attach event detection for all buttons."""
#         for key, pin in self.input_pins.items():
#             GPIO.add_event_detect(pin, GPIO.FALLING, callback=self.handle_input, bouncetime=200)

#     def handle_input(self, channel):
#         """Detect which button was pressed and trigger callback."""
#         for key, pin in self.input_pins.items():
#             if channel == pin:
#                 print(f"Key Pressed: {key}")  # Print to console
#                 if self.callback:
#                     self.callback(key)  # Call the user-defined function
#                 break

#     def cleanup(self):
#         """Cleanup GPIO when program exits."""
#         GPIO.cleanup()

# def check(key):
#     print(f"{key.ascii_lowercase()}")



# input_handler = InputHandler(check)
# try:
#     while True:
#         time.sleep(0.05)
# except KeyboardInterrupt:
#     print("Exiting...")
#     input_handler.cleanup()





from iohandler import InputHandler
from config import *
import time 
from PIL import Image
from interface import KeyBoard, CarouselMenu

def resize_image(path):
    original_image = Image.open(path).convert("1") 
    scale_factor = 0.4  # 50% scaling (264x300 → 132x150)
    scaled_width = int(original_image.width * scale_factor)
    scaled_height = int(original_image.height * scale_factor)
    scaled_image = original_image.resize((scaled_width, scaled_height), Image.Resampling.LANCZOS)

    oled_width, oled_height = 128, 64
    fitted_image = Image.new("1", (oled_width, oled_height), color=0) 

    x_offset = (oled_width - scaled_width) // 2  # Center horizontally
    y_offset = (oled_height - scaled_height) // 2  # Center vertically
    fitted_image.paste(scaled_image, (x_offset, y_offset))

    return fitted_image
    pass


io = InputHandler()
keyboard = KeyBoard(io, inpstr="password")


carousel = CarouselMenu(io, ["Wifi", "System", "Debug", "Bluetooth", "InputCheck", "bruhbruhlmao"])
try:
    # while True:
    #     curkey = io.GetCurrentKeyPress()
    #     if curkey == None:
    #         continue
    #     elif curkey == JS_U_PIN:
    #         io.DrawText((1,1), "up")
    #     elif curkey == JS_D_PIN:
    #         io.DrawText((1,1), "down")
    #     elif curkey == JS_R_PIN:
    #         io.DrawText((1,1), "right")
    #     elif curkey == JS_L_PIN:
    #         io.DrawText((1,1), "left")
    #     elif curkey == JS_P_PIN:
    #         # io.DrawText((1,1), "press")
    #         io.DrawImage(resize_image("./monochrome_undertale.jpg"))
    #     elif curkey == BTN1_PIN:
    #         io.DrawText((1,1), "btn1")
    #     elif curkey == BTN2_PIN:
    #         io.DrawText((1,1), "btn2")
    #     elif curkey == BTN3_PIN:
    #         io.DrawText((1,1), "btn3")
    #     time.sleep(0.05)
    # pass
    # keyboard.Interactive()
    carousel.Interactive()
except KeyboardInterrupt:
    print("Exitting ... ")
    io.GPIO_cleanup()
    exit(0)
