"""
Module wrapping around the W1ThermSensor package.
"""

import trio
from astroplant_kit.peripheral import Sensor

import w1thermsensor


class Ds18b20(Sensor):
    def __init__(self, *args, configuration):
        super().__init__(*args)

        self.measurement_interval = configuration["intervals"]["measurementInterval"]
        self.aggregate_interval = configuration["intervals"]["aggregateInterval"]

        sensor_type = (
            configuration["sensorType"] if "sensorType" in configuration else None
        )
        sensor_id = configuration["sensorId"] if "sensorId" in configuration else None

        self.w1ThermSensor = w1thermsensor.W1ThermSensor(
            sensor_type=sensor_type, sensor_id=sensor_id
        )

    async def measure(self):
        # w1thermsensor's get_temperature is blocking, and quite slow. Run it
        # in a thread and asynchronously await the result.
        temperature = await trio.to_thread.run_sync(self.w1ThermSensor.get_temperature)

        temperature_measurement = self.create_raw_measurement(
            "Temperature", "Degrees Celsius", temperature
        )
        return [temperature_measurement]
