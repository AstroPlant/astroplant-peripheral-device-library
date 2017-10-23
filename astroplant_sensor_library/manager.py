import asyncio

class SensorManager(object):
    def __init__(self):
        self.sensors = []
        self.subscribers = []

    async def run(self):
        await asyncio.wait([sensor.run() for sensor in self.sensors])

    def subscribe_physical_quantity(self, physical_quantity, callback):
        """
        Subscribe to messages concerning a specific physical quantity.
        :param physical_quantity: The name of the physical quantity for which the measurements are being subscribed to.
        :param callback: The callback to call with the measurement.
        """
        self.subscribe_predicate(lambda measurement: measurement.get_physical_quantity() == physical_quantity, callback)

    def subscribe_predicate(self, predicate, callback):
        """
        Subscribe to messages that conform to a predicate.
        :param predicate: A function taking as input a measurement and returning true or false.
        :param callback: The callback to call with the measurement.
        """
        self.subscribers.append((predicate, callback))

    def _publish_handle(self, measurement):
        for (predicate, callback) in self.subscribers:
            if predicate(measurement):
                callback(measurement)

    def add_sensor(self, sensor_class):
        sensor = sensor_class(self._publish_handle)
        self.sensors.append(sensor)
