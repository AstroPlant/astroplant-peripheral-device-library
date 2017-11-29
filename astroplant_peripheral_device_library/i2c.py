from time import sleep
import pigpio

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
        self.bus = bus
        self.address = address
        self.pi = pigpio.pi()
        
        # Open I2C handle
        self.handle = self.pi.i2c_open(self.bus, self.address)

    def read_byte(self):
        """
        Read a byte from the I2C device.

        :return: A byte read from the I2C device.
        """
        return self.pi.i2c_read_byte(self.handle)

    def write_byte(self, byte: int):
        """
        Write a byte to the I2C device.

        :param byte: The byte to write.
        """
        self.pi.i2c_write_byte(self.handle, byte)
        sleep(SLEEP_TIME)

    def read_byte_data(self, register: int):
        """
        Read a byte from the I2C device.

        :param register: The address of the register to read from.
        :return: A byte read from the I2C device.
        """
        return self.pi.i2c_read_byte_data(self.handle, register)

    def write_byte_data(self, register: int, data: int):
        """
        Write a data byte to a specified register on the I2C device.

        :param register: The address of the register to write to.
        :param data: The data byte to write.
        """
        self.pi.i2c_write_byte_data(self.handle, register, data)
        sleep(SLEEP_TIME)

    def read_word_data(self, register: int):
        """
        Read a word (two bytes) from the specified register on the I2C device.

        :param register: The address of the register to read from.
        :return: A word (two bytes) read from the I2C device.
        """
        return self.pi.i2c_read_word_data(self.handle, register)

    def write_word_data(self, register: int, data: int):
        """
        Write data word (two bytes) to the specified register on the I2C device.

        :param register: The address of the register to write to.
        :param data: The data word (two bytes) to write.
        """
        self.pi.i2c_write_byte_data(self.handle, register, data)
        sleep(SLEEP_TIME)

    def read_i2c_block_data(self, register: int, count: int):
        """
        Read a block of data from the I2C device.

        :param register: The address of the register to read from.
        :param length: The number of bytes to read.
        """
        return self.pi.i2c_read_i2c_block_data(self.handle, register, count)

    def write_i2c_block_data(self, register: int, data):
        """
        Write a list of data to the I2C device.

        :param register: The address of the register to write to.
        :param data: The list of data to write.
        """
        self.pi.i2c_write_i2c_block_data(self.handle, register, data)
        sleep(SLEEP_TIME)
