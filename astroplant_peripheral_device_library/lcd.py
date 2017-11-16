from time import sleep
from . import i2c
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
LCD_SET_CGRAM_ADDR = 0x40
LCD_SET_DDRAM_ADDR = 0x80

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

## Row offsets
LCD_ROW_OFFSETS = [0x80, 0xC0, 0x94, 0xD4,]

## RS/RW/EN bits
REGISTER_SELECT = 0x01
READ_WRITE = 0x02
ENABLE = 0x04

class LCD(Display):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.lines = []
        self.rows = 2
        self.columns = 16

        self.i2c_device = i2c.I2CDevice(0x27)

        # Set LCD to 2 lines, 5*8 character size, and 4 bit mode
        self.write_command(LCD_FUNCTION_SET | LCD_2_LINES | LCD_5x8_DOTS | LCD_4_BIT_MODE)

        self.clear()
        self.turn_on()
        self.home()

    def display(self, str):
        self.lines = [LCDLine(str) for str in str.splitlines()]
        self.clear()

    async def _run(self):
        for row in range(min(self.rows, len(self.lines))):
            line = self.lines[row]

            if line.len <= self.columns:
                # Line fits fully
                if not line.written:
                    self.set_cursor_position(row, 0)
                    self._write_str(line.str)
                    line.written = True
            else:
                # Line does not fit, scroll it continuously

                # Get cursor position on screen, based on current index in the line
                cursor_position = max(self.columns - line.idx - 1, 0)

                # Get the length of the line we can print on
                line_length = self.columns - cursor_position

                # Get the text to display
                text = line.str[line.idx-(line_length-1):line.idx+1]
                prepend_spaces = " " * cursor_position
                append_spaces = " " * (line_length - len(text))

                # Set the cursor position and display
                self.set_cursor_position(row, 0)
                self._write_str(prepend_spaces + text + append_spaces)

                line.idx += 1

                # Text is now empty, so we are at the end of the line. Reset back to start
                if len(text) == 0:
                    line.idx = 0

        await asyncio.sleep(0.25)

    def _write_str(self, str):
        for char in str:
            self.write_char(ord(char))

    def _pulse_data(self, data: int):
        """
        Pulse the Enable flag to send data.

        :param data: The data to send.
        """
        if self.backlight:
            data |= LCD_BACKLIGHT_ON
        else:
            data |= LCD_BACKLIGHT_OFF
        
        self.i2c_device.write_byte(data | ENABLE)
        sleep(0.0005)
        self.i2c_device.write_byte(data & ~ENABLE)
        sleep(0.0001)

    def write_command(self, command: int):
        # Send first four bits
        self._pulse_data(command & 0xF0)
        # Send last four bits
        self._pulse_data((command << 4) & 0xF0)

    def write_char(self, char: int):
        # Send first four bits
        self._pulse_data(REGISTER_SELECT | (char & 0xF0))
        # Send last four bits
        self._pulse_data(REGISTER_SELECT | ((char << 4) & 0xF0))

    def clear(self):
        self.write_command(LCD_CLEAR_DISPLAY)

    def home(self):
        self.write_command(LCD_RETURN_HOME)

    def set_cursor_position(self, row=0, column=0):
        row = min(row, len(LCD_ROW_OFFSETS))
        self.write_command(LCD_SET_DDRAM_ADDR | (column + LCD_ROW_OFFSETS[row]))

    def turn_on(self):
        self.write_command(LCD_DISPLAY_CONTROL | LCD_DISPLAY_ON)

    def turn_off(self):
        self.write_command(LCD_DISPLAY_CONTROL | LCD_DISPLAY_OFF)

    def scroll_right(self):
        self.write_command(LCD_CURSOR_SHIFT | LCD_DISPLAY_MOVE | LCD_MOVE_RIGHT)

    def scroll_left(self):
        self.write_command(LCD_CURSOR_SHIFT | LCD_DISPLAY_MOVE | LCD_MOVE_LEFT)

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

class LCDLine(object):
    def __init__(self, str):
        self.str = str
        self.len = len(str)
        self.idx = 0
        self.written = False
