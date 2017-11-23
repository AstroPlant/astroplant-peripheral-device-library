# http://eleparts.co.kr/data/design/product_file/SENSOR/gas/MH-Z19_CO2%20Manual%20V2.pdfasd# http://qiita.com/UedaTakeyuki/items/c5226960a7328155635f
import serial
from astroplant_kit.peripheral import *

class MHZ19(Sensor):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serial = serial.Serial('/dev/ttyS0',
                                    baudrate=9600,
                                    bytesize=serial.EIGHTBITS,
                                    parity=serial.PARITY_NONE,
                                    stopbits=serial.STOPBITS_ONE,
                                    timeout=1.0)

    async def measure(self):
        command = "\xff\x01\x86\x00\x00\x00\x00\x00\x79"
        result=self.serial.write(bytes(command, 'latin1'))

        s = self.serial.read(9)
        s = s.decode('latin1')

        co2_concentration = ord(s[2])*256 + ord(s[3])
        measurement = Measurement(self, "Concentration", "Parts per million", co2_concentration)

        return measurement
