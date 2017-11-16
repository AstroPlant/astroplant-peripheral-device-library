import i2c
import asyncio
from astroplant_kit.peripheral import *

# I2C device constants
## Commands
LCD_CLEAR_DISPLAY = 0x01
LCD_RETURN_HOME = 0x02
LCD_ENTRY_MODE_SET = 0x04
LCD_DISPLAY_CONTROL = 0x08
LCD_CURSOR_SHIFT = 0x10
LCD_FUNCTION_SET = 0x20
LCD_SETCGRAMADDR = 0x40
LCD_SETDDRAMADDR = 0x80

## Entry mode flags
LCD_ENTRY_RIGHT = 0x00
LCD_ENTRY_LEFT = 0x02
LCD_ENTRY_SHIFT_INCREMENT = 0x01
LCD_ENTRY_SHIFT_DECREMENT = 0x00

## Display control flags
LCD_DISPLAY_ON = 0x04
LCD_DISPLAY_OFF = 0x00
LCD_CURSOR_ON = 0x02
LCD_CURSOR_OFF = 0x00
LCD_BLINK_ON = 0x01
LCD_BLINK_OFF = 0x00

## Backlight control flags
LCD_BACKLIGHT_ON = 0x08
LCD_BACKLIGHT_OFF = 0x00

## Display shift flags
LCD_DISPLAY_MOVE = 0x08
LCD_CURSOR_MOVE = 0x00
LCD_MOVE_RIGHT = 0x04
LCD_MOVE_LEFT = 0x00

## Function set flags
LCD_8_BIT_MODE = 0x10
LCD_4_BIT_MODE = 0x00
LCD_2_LINES = 0x08
LCD_1_LINE = 0x00
LCD_5x10_DOTS = 0x04
LCD_5x8_DOTS = 0x00

## RS/RW/EN bits
REGISTER_SELECT = 0x01
READ_WRITE = 0x02
ENABLE = 0x04

class LCD(Display):

    def display(self, str):
        self.i2c_device = i2c.I2CDevice(0x27)

        # Set LCD to 2 lines, 5*8 character size, and 4 bit mode
        self.i2c_device.write_byte(LCD_FUNCTION_SET | LCD_2_LINES | LCD_5x8_DOTS | LCD_4_BIT_MODE)

        # Clear the LCD display
        self.i2c_device.write_cmd(LCD_CLEAR_DISPLAY)

        # Turn LCD display on
        self.i2c_device.write_cmd(LCD_DISPLAY_CONTROL | LCD_DISPLAY_ON)

    def backlight(self, state: bool):
        """
        Turn the backlight on or off.

        :param state: back light status to set
        """
        self.backlight = state
        if state:
            self.i2c_device.write_cmd(LCD_BACKLIGHT_ON)
        else:
            self.i2c_device.write_cmd(LCD_BACKLIGHT_OFF)
