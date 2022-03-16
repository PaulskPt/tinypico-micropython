Tiny Snake on the TinyPICO
==========================

Just copy all of these files over to your TinyPICO and reset it and it will launch snake.

A part of the game code is in main.py

Update 2022-03-16 

This is a forked/modified version by @PaulskPt

It is specially adapted for the TinyPICO IPS DISPLAY SHIELD (contains a ST7735 LCD),
but it can also be used with ssd1306 and sh1107 type of displays.

The game is not using a 'Play shield' (end of life reached?). It uses 3 external buttons
connected to certain pins of the TinyPICO.

The 'class Snake' has been taken out of main.py and put in a separate file: snake.py

Main.py has various global 'flags' to indicate which of certain models of displays 
are being used for the snake game: 
The types of displays are devided into two groups:
- a) on oled group: sh1107 and ssd1306 (i2c - oled);
- b) a tft group:   st7735 (spi - tft).

Other global 'flags':
- my_debug;    a flag that is used for print statements during the development stage
- use_pullup;  a flag that is used for the i2c devices;
- use_btn4;    self evident. Set to True if one uses a fourth button
- use_sound.   self evident. Set to True is uses sound.

File st7735.py copied from:  https://github.com/boochow/MicroPython-ST7735/blob/master/ST7735.py
The 'class TFT' in file: st7735 .py has various functions added:
set_size();
get_rotation();
get_offset();
set_offset().
renamed function size() into get_size().
Added some other minor changes in st7735.py. They are mentioned in the heading of that file.

