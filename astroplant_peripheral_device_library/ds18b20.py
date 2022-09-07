"""
Module wrapping around the W1ThermSensor package.
"""

import trio
from astroplant_kit.peripheral import (
    Sensor,
    FatalPeripheralError,
    TemporaryPeripheralError,
)

import w1thermsensor


class Ds18b20(Sensor):
    def __init__(self, *args, configuration):
        super().__init__(*args)

        self.measurement_interval = configuration["intervals"]["measurementInterval"]
        self.aggregate_interval = configuration["intervals"]["aggregateInterval"]

        self.sensor_type = (
            configuration["sensorType"] if "sensorType" in configuration else None
        )
        self.sensor_id = (
            configuration["sensorId"] if "sensorId" in configuration else None
        )

    async def set_up(self):
        def _set_up():
            return w1thermsensor.W1ThermSensor(
                sensor_type=self.sensor_type, sensor_id=self.sensor_id
            )

        try:
            self.sensor = await trio.to_thread.run_sync(_set_up)
        except Exception as e:
            raise FatalPeripheralError("could not set up sensor") from e

    async def measure(self):
        # w1thermsensor's get_temperature is blocking, and quite slow. Run it
        # in a thread and asynchronously await the result.
        try:
            temperature = await trio.to_thread.run_sync(self.sensor.get_temperature)
        except Exception as e:
            raise TemporaryPeripheralError("failed to read from sensor") from e

        temperature_measurement = self.create_raw_measurement(
            "Temperature", "Degrees Celsius", temperature
        )
        return [temperature_measurement]
