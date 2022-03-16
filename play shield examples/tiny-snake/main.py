# The MIT License (MIT)
#
# Copyright (c) 2019 Seon "Unexpected Maker" Rozenblum
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
`tinypico-playshield-snake` - Snake Game for the TinyPICO Play Shield
=====================================================================
* Author(s): Seon Rozenblum
* Mods by: Paulus Schulinck (@paulskpt)
* TinyPico V2 with MicroPython v1.18
* Most recent test with SH1107 display: 2022-03-14. Works OK. 
* Most recent test with ST7735 display: 2022-03-15. Works OK. Only remark: tft.WHITE gives a black backgrond and viceversa.

Pins Used for display:

SPI
SCK  Pin(18) # hardware wired (see schematic)
MOSI Pin(23) # idem
MISO Pin(19) # idem  (internal not connected)

TFT
DC  Pin(15) # hardware wired (see schematic)
RST Pin(9)  # idem
LED Pin(14) # idem

I2C
SCL Pin(22)
SDA Pin(21))

PWM
PWM Pin(25)  # Sound pin

Buttons:
BUT_1 Pin(26)
BUT_2 Pin(27)
BUT_3 Pin(4)
BUT_4 Pin(5) # not used

"""

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/unexpectedmaker/tinypico"

my_debug = True
use_sh1107 = False
use_ssd1306 = False
use_st7735 = True

use_pullup = True
use_btn4 = False
use_sound = False

from machine import Pin, Timer, PWM, SoftI2C
import time, random, framebuf, math
import bitmaps, notes
from snake import Snake

oled = None
tft = None

# Globals for sound
PWM_PIN = 25
PWM_FREQ = 20000
PWM_DUTY = 512

if use_sh1107:
    #from machine import SoftI2C
    import sh1107

if use_st7735:
    from machine import SPI
    from st7735 import TFT
    from sysfont import sysfont
    
import tinypico_helper as TinyPICO
from micropython import const

# Turn off the power to the DotStar
TinyPICO.set_dotstar_power( False )

# Globals
if use_sh1107:
    disp_width  = 128
    disp_height =  64

if use_ssd1306:
    disp_width  = 160
    disp_height  = 80
    
if use_st7735:
    disp_width  = 240
    disp_height = 120

yofs = {0: 20, 1: disp_height//2, 2: disp_height-20}

snake = None
game_state = -1 #0 = menu, 1 = playing, 2 = pause, 3 = gameover
game_state_changed = False
snake_start = None  # tuple(h, v)
fruit_interval = 10
fruit_next = 0
default_freq = 1
dflt_bg = None
text_color = None

# Buttons
BUT_1 = Pin(26, Pin.IN )
BUT_2 = Pin(27, Pin.IN )
BUT_3 = Pin(15, Pin.IN )
BUT_4 = Pin(14, Pin.IN )

# Buttons

BUT_1 = Pin(26, Pin.IN, Pin.PULL_UP if use_pullup else Pin.PULL_DOWN)
BUT_2 = Pin(27, Pin.IN, Pin.PULL_UP if use_pullup else Pin.PULL_DOWN)
BUT_3 = Pin(33, Pin.IN, Pin.PULL_UP if use_pullup else Pin.PULL_DOWN)
if use_btn4:
    BUT_4 = Pin(32, Pin.IN if use_pullup else Pin.PULL_DOWN)

last_button_pressed = 0
last_button_press_time = 0

# create timer for flashing UI
flasher = Timer(0)
flash_state = False
# Begin

# Turn off the power to the DotStar
TinyPICO.set_dotstar_power( False )

#i2c = I2C(scl=Pin(22), sda=Pin(21))
# Configure I2C for controlling anything on the I2C bus
# Software I2C only for this example but the next version of MicroPython for the ESP32 supports hardware I2C too
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
print("TinyPICO Snake Game startup")
print("type(i2c) = ", type(i2c))
devices = i2c.scan()
if len(devices) == 0:
    print("No i2c device !")
else:
    print("i2c devices found: ", len(devices))
    
    for device in devices:
        print("Decimal address:  {:3d} | Hex address: {:3s}".format(device, hex(device)))
        if device == 60:
            print("Adafruit Feather SH1107 OLED display connected via I2C")
        elif device == 0x6f:
            print("UM RTC shield connected via I2C")

if use_sh1107:
    # Initialise the OLED screen
    oled = sh1107.SH1107_I2C(disp_width, disp_height, i2c)

if use_ssd1306:
    oled = ssd1306.SSD1306_I2C(disp_width, disp_height, i2c)  # was: (128, 64, i2c)
    
if use_st7735:
    spi = SPI(2, baudrate=20000000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
    # Add the TP logo to a frameBuf buffer and show it for 2 seconds
    # Create tft object
    tft = TFT(spi, 15, 9, 5, 240, 120)  # DC Pin(15),  Reset Pin(9), CS Pin(5), 160 display width, 80 display height
    tft.rgb(True)
    dflt_bg = tft.BLACK
    text_color = tft.WHITE
    print("default background color = 0x{:x}".format(dflt_bg))
    tft.rotation(3)  # rotation = 270 degs
    print("Rotation is set to: ", tft.get_rotation())
    tft.initg()
    print("Current display offset: ", tft.get_offset())
    #tft.set_offset(40, 20)  # (240-160)/2, (120-80)/2
    #tft.invertcolor(True)
    # get the display dimensions received by TFT class
    disp_height = tft.get_size()[0] # set the global vars accordingly
    disp_width = tft.get_size()[1]  # idem
    yofs = {0: 20, 1: disp_height//2, 2: disp_height-20}
    tft.fill(dflt_bg)
    #tft.fill(tft.MAROON)
    if my_debug:
        print("Size received from TFT: width = {}, height = {}".format(tft.get_size()[0], tft.get_size()[1]))

#snake_start = set_snake_startpos() # (disp_width//2, disp_height//2)
# Add the TP logo to a frameBuf buffer and show it for 2 seconds    
fbuf = framebuf.FrameBuffer(bytearray(bitmaps.icon_tinypico), disp_width, disp_height, framebuf.MONO_HLSB)

# Sound
def play_boot_music():
    global default_freq
    speaker = PWM(Pin(PWM_PIN), freq=PWM_FREQ, duty=PWM_DUTY)
    boot_sound = [notes.D4, 0, notes.G4, 0, notes.D4, 0, notes.A4, 0]
    for i in boot_sound:
        if i == 0:
            speaker.freq(default_freq) # When 0 ValueError: frequency must be from 1Hz to 40MHz
            time.sleep_ms(50)
            pass
        else:
            speaker.freq(i)
            time.sleep_ms(250)

    speaker.freq(default_freq) # When (0) ValueError: frequency must be from 1Hz to 40MHz
    speaker.deinit()

def play_death():
    global default_freq
    speaker = PWM(Pin(PWM_PIN), freq=PWM_FREQ, duty=PWM_DUTY)
    speaker.freq(notes.D4)
    time.sleep_ms(200)
    speaker.freq(default_freq)  # when 0 ValueError: freqency must be from 1Hz to 40MHz
    time.sleep_ms(25)
    speaker.freq(notes.A2)
    time.sleep_ms(400)
    speaker.freq(default_freq) 
    speaker.deinit()

def play_sound( note, duration ):
    global default_freq
    speaker = PWM(Pin(PWM_PIN), freq=PWM_FREQ, duty=PWM_DUTY)
    speaker.freq(note)
    time.sleep_ms(duration)
    speaker.freq(default_freq)  # when 0 ValueError: freqency must be from 1Hz to 40MHz
    speaker.deinit()

def switch_state( new_state ):
    global game_state, game_state_changed
    if game_state == new_state:
        pass
    else:
       game_state = new_state
       game_state_changed = True

def player_turn(dir):
    global snake
    snake.set_dir(dir)

# Helpers

def process_button_1():
    global game_state, last_button_pressed
    last_button_pressed = 1
    if my_debug:
        print("Button 1 pressed")
    if game_state == 1:
        player_turn(1)

def process_button_2():
    global game_state, last_button_pressed
    last_button_pressed = 2
    if my_debug:
        print("Button 2 pressed")
    if game_state == 0:
        switch_state(1)
    elif game_state == 3:
        switch_state(0)

def process_button_3():
    global game_state, last_button_pressed
    last_button_pressed = 3
    if my_debug:
        print("Button 3 pressed")
    if game_state == 1:
        player_turn(-1)

def process_button_4():
    global game_state, last_button_pressed
    last_button_pressed = 4
    print("Pressed Button ", last_button_pressed)

def button_press_callback(pin):
    global last_button_press_time, last_button_pressed
    #if my_debug:
    #    print("Last button pressed: ", last_button_pressed)
    # block button press as software debounce
    last_button_pressed = 0 # reset
    if last_button_press_time < time.ticks_ms():
        
        # add 150ms delay between button presses... might be too much, we'll see!
        last_button_press_time = time.ticks_ms() + 150

        # If the pin is in the callback handler dictionary, call the appropriate function 
        if str(pin) in button_handlers:
            button_handlers[str(pin)]()
    # else:
    #     # print a debug message if button presses were too quick or a dounce happened
    #     print("Button Bounce - {}ms".format( ( last_button_press_time - time.ticks_ms() ) ) )

button_handlers = { str(BUT_1): process_button_1, str(BUT_2): process_button_2, str(BUT_3):process_button_3, str(BUT_4): process_button_4 }
# Create all of the triggers for each button pointing to the single callback handler
BUT_1.irq(trigger=Pin.IRQ_FALLING, handler=button_press_callback)
BUT_2.irq(trigger=Pin.IRQ_FALLING, handler=button_press_callback)
BUT_3.irq(trigger=Pin.IRQ_FALLING, handler=button_press_callback)
BUT_4.irq(trigger=Pin.IRQ_FALLING, handler=button_press_callback)

def flasher_update(timer):
    global flash_state
    flash_state = not flash_state

def flash_text(x,y,text):
    global oled, tft, flash_state, sysfont, text_color

    if flash_state:
        if use_sh1107 or use_ssd1306:
            oled.text(text, x, y, 2)
        else:
            tft.text((x,y), text, text_color, sysfont)
    else:
        if use_sh1107 or use_ssd1306:     
            oled.fill_rect( 1, y, 126, 12, 0)
        else:
            tft.fillrect((1,y), (126,12), dflt_bg)
            
def text_horiz_centred(fb, text, y, char_width=8):
    global text_color, sysfont
    if use_st7735:
        dw = 180 # tft.get_size()[0]
    
    if use_sh1107 or use_ssd1306:
        w = fb.width
        fb.text(text, (w - len(text) * char_width) // 2, y)
    else:
        w = dw # was: tft.get_size()[0]
        fb.text( ((w - len(text) * char_width) // 2, y), text, text_color, sysfont)

def show_menu():
    global oled, tft, dflt_bg, text_color
    # clear the display
    if use_sh1107 or use_ssd1306:
        oled.fill(0)
        fb = oled
    else:
        fb = tft
        tft.fill(dflt_bg)
    # Show welcome message
    text_horiz_centred( fb, "TINY SNAKE",35 )
    text_horiz_centred( fb, "3-Left  1-Right", 50 )
    if use_sh1107 or use_ssd1306:
        oled.line(0, 12, 127, 12,1 )
        # oled.text("TINY SNAKE", 25, 0, 2)
        # oled.text("3-Left  1-Right", 4, 50, 2) 
        oled.show()
    else:
        tft.vline((0,80), 127, text_color)
        #tft.line((12, 0), (12, 127), text_color)

def draw_snake():
    global oled, tft, snake, fruit_next, fruit_interval
    # Move the snake and return if we need to clear the tail or if the snake grew
    result = snake.move()
    # The snake tail position is stored in result index 0,1 if it needs to be removed
    # If x or y are > 0 then we reove that pos from the screen
    if result[0] > 0 or result[1] > 0:
        if use_sh1107 or use_ssd1306:
            oled.fill_rect(result[0], result[1], 2, 2, 0)
        else:
            tft.fillrect((result[0], result[1]), (2,2), dflt_bg)
    # The last eaten fruit position is stored in indexs 2,3 if it needs to be removed
    # If x or y are > 0 then we reove that pos from the screen
    if result[2] > 0 or result[3] > 0:
        if use_sh1107 or use_ssd1306:
            oled.fill_rect(result[2]-1, result[3]-1, 3, 3, 0)
        else:
            tft.fillrect((result[2]-1, result[3]-1), (3,3), dflt_bg)
        play_sound(notes.C4,100)

    # Go through the snake positions and draw them
    for pos in snake.get_positions():
        if use_sh1107 or use_ssd1306:
            oled.fill_rect(pos[0], pos[1], 2, 2, 1)
        else:
            tft.fillrect((pos[0], pos[1]), (2,2), dflt_bg)
    # Redraw all fruit
    for pos in snake.get_fruit_positions():
        if use_sh1107 or use_ssd1306:   
            oled.fill_rect(pos[0]-1, pos[1]-1, 3, 3, 1)
        else:
            tft.fillrect((pos[0]-1, pos[1]-1), (3,3), dflt_bg)
    # Update the OLED
    if use_sh1107 or use_ssd1306:
        oled.show()
    time.sleep( snake.get_speed() )

    # If the snake died in that move, end the game
    if snake.is_dead():
        play_death()
        switch_state( 3 )

def setup_new_game():
    global oled, tft, disp_width, disp_height, dflt_bg
    if use_sh1107 or use_ssd1306:
        oled.fill(0)
        oled.rect(0, 0, disp_width, disp_height, 1)
        # oled.rect(1, 1, 127, 63, 1)
        oled.show()
    else:
        tft.fill(tft.WHITE) #dflt_bg)
        print("setup_new_game(): disp_width: {}, disp_height: {}".format(disp_height, disp_width))
        dw = 240
        dh = 120
        tft.rect((0,0),(disp_height, disp_width), tft.WHITE)

    #reset variables
    global snake, fruit_next, fruit_interval, snake_start
    hor = 0
    vert = 1
    
    snake_start = set_snake_startpos() # generate a random start position
    snake.reset( x=snake_start[hor], y=snake_start[vert], len=3, dir=0 )

    fruit_next = time.time() + fruit_interval

    draw_snake()

def show_gameover():
    global snake, oled, tft
    if use_sh1107 or use_ssd1306:
        oled.fill(0)
        fb = oled
    else:
        tft.fill(dflt_bg)
        fb = tft
    text_horiz_centred( fb, "YOU SCORED " + str( snake.get_score() ), 35 )
    text_horiz_centred( fb, "2 - Continue", 50 )
    # oled.text("YOU SCORED " + str( snake.get_score() ), 10, 10, 2)
    # oled.text("2 - Continue", 15, 50, 2)
    if use_sh1107 or use_ssd1306:
        oled.show()

def set_snake_startpos():
    global snake_start
    if my_debug:
        print("set_snake_startpos(): disp_width {}, disp_height {}".format(disp_width, disp_height))
    if use_sh1107 or use_ssd1306:
        x = random.randint(5, disp_width-5)
        y = random.randint(5, disp_height-5)
    else:
        x = random.randint(5, 160)
        y = random.randint(5, 80)
    print("random start position: ", (x,y))
    return (x, y)
    
def main():
    global oled, tft, snake, game_state_changed, disp_width, disp_height, snake_start
    
    flasher.init(period=500, mode=Timer.PERIODIC, callback=flasher_update)
    # Create an instance of Snake
    len = 6
    dir = 0
    snake_start = set_snake_startpos() # generate a random start position
    snake = Snake( disp_width, disp_height, snake_start[0], snake_start[1], len, dir )
    
    if use_sh1107 or use_ssd1306:
        oled.blit(fbuf, 0, 2)
        fb = oled
    else:
        fb = tft
    text_horiz_centred( fb, "PLAY SHIELD", 35)
    text_horiz_centred( fb, "INTEL NOT INSIDE", 50)
    
    if use_sh1107 or use_ssd1306:
        oled.show()
    play_boot_music()
    time.sleep(2)
    # show the menu on start
    switch_state(0)
    
    while True:
        try:
            if game_state_changed:
                game_state_changed = False

                if game_state == 0:
                    show_menu()
                elif game_state == 1:
                    setup_new_game()
                elif game_state == 3:
                    show_gameover()

            # menu
            if game_state == 0:
                flash_text( 26, 70, "Press 2 to start")
                if use_sh1107 or use_ssd1306:
                    oled.show()
                time.sleep(.001)

            elif game_state == 1:
                draw_snake()

            elif game_state == 3:
                flash_text( 52, 70, "GAME OVER")
                if use_sh1107 or use_ssd1306:
                    oled.show()
                time.sleep(.001)
        except KeyboardInterrupt:
            raise SystemExit

main()   





