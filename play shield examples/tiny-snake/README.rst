Tiny Snake on the TinyPICO Play Shield
======================================

Just copy all of these files over to your TinyPICO and reset it and it will launch snake.

All of the game code is in main.py

Update 2022-03-16 

This is a forked/modified version by @PaulskPt

Adapted for the TinyPICO ISP DISPLAY SHIELD (contains a ST7735).

The game is not using an (obscelete) 'Play shield' but 3 external buttons
connected to the TinyPICO.

Also the 'class Snake' has been taken out of main.py and put in a separate snake.py

Main.py has various global 'flags' to indicate if certain displays are being used for
the snake game: 
- the group: sh1107 and ssd1306 (i2c - oled);
- the st7735 (spi - tft).

Other global 'flags':
- my_debug;    a flag that is used for print statements during the development stage
- use_pullup;  a flag that is used for the i2c devices;
- use_btn4;    self evident. Needed if one uses a fourth button
- use_sound.   self evident. 
