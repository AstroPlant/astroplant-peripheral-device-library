"""
Module wrapping around the W1ThermSensor package.
"""

import asyncio
from astroplant_kit.peripheral import *

import w1thermsensor

class W1ThermSensor(Sensor):

    def __init__(self, *args, sensor_type, sensor_id, **kwargs):
        super().__init__(*args, **kwargs)
        
        if sensor_type == "None":
            sensor_type = None
        if sensor_id == "None":
            sensor_id = None
        
        self.w1ThermSensor = w1thermsensor.W1ThermSensor(sensor_type = sensor_type, sensor_id = sensor_id)

    async def measure(self):
        # w1thermsensor's get_temperature is blocking, and quite slow. Run it in a separate thread
        # and asynchronously await the result.
        loop = asyncio.get_event_loop()
        temperature = await loop.run_in_executor(None, self.w1ThermSensor.get_temperature)

        temperature_measurement = Measurement(self, "Temperature", "Degrees Celsius", temperature)
        return [temperature_measurement,]
