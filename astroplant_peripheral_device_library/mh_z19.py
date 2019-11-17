# http://eleparts.co.kr/data/design/product_file/SENSOR/gas/MH-Z19_CO2%20Manual%20V2.pdf
# http://qiita.com/UedaTakeyuki/items/c5226960a7328155635f
import serial
from astroplant_kit.peripheral import Sensor


class MhZ19(Sensor):

    #: Amount of time in seconds to wait between making measurements
    TIME_SLEEP_BETWEEN_MEASUREMENTS = 1.0

    #: Amount of time in seconds over which measurements are reduced before publishing them for storage
    TIME_REDUCE_MEASUREMENTS = 300.0

    def __init__(self, *args, configuration):
        super().__init__(*args)

        self.measurement_interval = configuration["intervals"]["measurementInterval"]
        self.aggregate_interval = configuration["intervals"]["aggregateInterval"]

        file_name = (
            configuration["serialFile"]
            if "serialFile" in configuration
            else "/dev/ttyS0"
        )
        self.serial = serial.Serial(
            "/dev/ttyS0",
            baudrate=9600,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1.0,
        )

    async def measure(self):
        command = "\xff\x01\x86\x00\x00\x00\x00\x00\x79"
        result = self.serial.write(bytes(command, "latin1"))

        s = self.serial.read(9)
        s = s.decode("latin1")

        co2_concentration = ord(s[2]) * 256 + ord(s[3])
        measurement = self.create_raw_measurement(
            "Concentration", "Parts per million", co2_concentration
        )

        return measurement
