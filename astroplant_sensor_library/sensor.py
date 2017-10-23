import abc
import asyncio

class Sensor(object):
    """
    Abstract sensor base class.
    """

    def __init__(self, publish_handle):
        self._publish_handle = publish_handle

    @asyncio.coroutine
    def run(self):
        while True:
            measurement = yield from self.measure()
            asyncio.ensure_future(self._publish_measurement(measurement))

    @abc.abstractmethod
    @asyncio.coroutine
    def measure(self):
        raise NotImplementedError()

    @asyncio.coroutine
    def _publish_measurement(self, measurement):
        self._publish_handle(measurement)

class Measurement(object):
    def __init__(self, sensor, physical_quantity, physical_unit, value):
        self.sensor = sensor
        self.physical_quantity = physical_quantity
        self.physical_unit = physical_unit
        self.value = value

    def get_sensor(self):
        return self.sensor

    def get_physical_quantity(self):
        return self.physical_quantity

    def get_physical_unit(self):
        return self.get_physical_unit

    def get_value(self):
        return self.value

    def __str__(self):
        return "%s %s: %s %s" % (self.sensor, self.physical_quantity, self.value, self.physical_unit)
