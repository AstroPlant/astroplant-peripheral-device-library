import pigpio
from astroplant_kit.peripheral import Actuator


class Pwm(Actuator):
    def __init__(self, *args, configuration):
        super().__init__(*args)

        self.pins = configuration["gpioAddresses"]
        self.pi = pigpio.pi()
        for pin in self.pins:
            self.pi.set_PWM_range(pin, 100)

    async def clean_up(self):
        self.pi.stop()

    def _intensity_transform(self, intensity):
        return intensity

    async def do(self, command):
        if "intensity" in command:
            intensity = command["intensity"]
            for pin in self.pins:
                self.pi.set_PWM_dutycycle(pin, self._intensity_transform(intensity))


class Fans(Pwm):
    def _intensity_transform(self, intensity):
        """
        Clamp intensity to values where the fans are either off or will
        actually likely rotate.
        """
        # TODO make this configurable
        MIN_ROTATE_INTENSITY = 50.0
        if intensity < MIN_ROTATE_INTENSITY / 2:
            return 0.0
        else:
            return max(MIN_ROTATE_INTENSITY, intensity)
