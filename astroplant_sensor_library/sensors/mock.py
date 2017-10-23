import asyncio
import random
import astroplant_sensor_library.sensor

class Mock(astroplant_sensor_library.sensor.Sensor):
    """
    A mock sensor implementation yielding fake measurements.
    """

    async def measure(self):
        temperature = random.uniform(19, 22)
        measurement = astroplant_sensor_library.sensor.Measurement(self, "Temperature", "Degrees Celsius", temperature)
        await asyncio.sleep(5)
        return measurement
