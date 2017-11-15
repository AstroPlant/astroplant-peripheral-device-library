import asyncio
import random
from astroplant_kit.peripheral import *

class Mock(Sensor):
    """
    A mock sensor implementation yielding fake measurements.
    """

    def __init__(self, *args, sleep):
        super().__init__(*args)
        self.sleep = int(sleep)

    async def measure(self):
        import random

        temperature = random.uniform(19, 22)
        pressure = random.uniform(0.98, 1.02)

        temperature_measurement = Measurement(self, "Temperature", "Degrees Celsius", temperature)
        pressure_measurement = Measurement(self, "Pressure", "Bar", pressure)

        await asyncio.sleep(self.sleep / 1000)
        return [temperature_measurement, pressure_measurement]
