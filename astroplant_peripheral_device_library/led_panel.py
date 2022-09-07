import pigpio
from astroplant_kit.peripheral import Actuator


class LedPanel(Actuator):
    def __init__(self, *args, configuration):
        super().__init__(*args)

        self._blue_pin = configuration["gpioAddressBlue"]
        self._red_pin = configuration["gpioAddressRed"]
        self._far_red_pin = configuration["gpioAddressFarRed"]

        self.pi = pigpio.pi()
        self.pi.set_PWM_range(self._blue_pin, 100)
        self.pi.set_PWM_range(self._red_pin, 100)
        self.pi.set_PWM_range(self._far_red_pin, 100)

    async def clean_up(self):
        self.pi.stop()

    async def do(self, command):
        if "blue" in command:
            self.pi.set_PWM_dutycycle(self._blue_pin, command["blue"])
        if "red" in command:
            self.pi.set_PWM_dutycycle(self._red_pin, command["red"])
        if "farRed" in command:
            self.pi.set_PWM_dutycycle(self._far_red_pin, command["farRed"])
