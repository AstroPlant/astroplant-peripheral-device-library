import pigpio
from astroplant_kit.peripheral import Actuator


class Pwm(Actuator):
    def __init__(self, *args, configuration):
        super().__init__(*args)

        self.pins = configuration["gpioAddresses"]
        self.pi = pigpio.pi()
        for pin in self.pins:
            self.pi.set_PWM_range(pin, 100)

    async def do(self, command):
        intensity = command
        for pin in self.pins:
            self.pi.set_PWM_dutycycle(pin, intensity)
