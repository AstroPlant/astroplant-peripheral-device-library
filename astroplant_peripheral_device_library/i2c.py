import smbus
from time import sleep

"""
SMBus protocol summary:

https://www.kernel.org/doc/Documentation/i2c/smbus-protocol
"""

SLEEP_TIME = 0.0001

class I2CDevice(object):
    
    def __init__(self, address, bus = 1):
        """
        Initialize the I2C device.

        Raspberry Pi revision 2, Raspberry Pi 2 & Raspberry Pi 3 use bus 1
        Raspberry Pi revision 1 uses bus 0
        """
        self.address = address
        self.bus = smbus.SMBus(bus)

    def read_byte(self):
        """
        Read a byte from the I2C device.

        :return: A byte read from the I2C device.
        """
        return self.bus.read_byte(self.address)

    def write_byte(self, byte: int):
        """
        Write a byte to the I2C device.

        :param byte: The byte to write.
        """
        self.bus.write_byte(self.address, byte)
        sleep(SLEEP_TIME)

    def read_byte_data(self, command: int):
        """
        Read a byte from the I2C device.

        :param command: The command byte.
        :return: A byte read from the I2C device.
        """
        return self.bus.read_byte_data(self.address, command)

    def write_byte_data(self, command: int, data: int):
        """
        Write a command and data byte to the I2C device.

        :param command: The command byte to write.
        :param data: The data byte to write.
        """
        self.bus.write_byte_data(self.address, command, data)
        sleep(SLEEP_TIME)

    def read_word_data(self, command: int):
        """
        Read a word (two bytes) from the I2C device.

        :param command: The command byte.
        :return: A word (two bytes) read from the I2C device.
        """
        return self.bus.read_word_data(self.address, command)

    def write_word_data(self, command: int, data: int):
        """
        Write a command byte and data word (two bytes) to the I2C device.

        :param command: The command byte to write.
        :param data: The data word (two bytes) to write.
        """
        self.bus.write_byte_data(self.address, command, data)
        sleep(SLEEP_TIME)
