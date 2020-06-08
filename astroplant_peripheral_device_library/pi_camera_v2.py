import logging
import threading
import io
import trio
import time
import atexit
import pigpio
import picamera
import numpy as np
from PIL import Image
from fractions import Fraction

from astroplant_kit.peripheral import Peripheral, PeripheralCommandResult

from .led_panel import LedPanel
from typing import Iterable


logger = logging.getLogger("astroplant_peripheral_device_library.pi_camera_v2")

# requires:
# sudo apt install libpng12-dev
# sudo apt install libatlas-base-dev


class UnknownCamera(ValueError):
    pass


class Incompatable(Exception):
    pass


class Command:
    UNCONTROLLED = "UNCONTROLLED"
    REGULAR = "REGULAR"
    NIR = "NIR"
    NDVI = "NDVI"


def _find_led_panel(peripherals: Iterable[Peripheral]):
    for peripheral in peripherals:
        if isinstance(peripheral, LedPanel):
            return peripheral


def _capture(camera: picamera.PiCamera) -> bytes:
    """
    Capture an image to png.
    """
    bytes_stream = io.BytesIO()
    camera.capture(bytes_stream, "png")
    bytes_stream.seek(0)
    return bytes_stream.read()


async def _capture_uncontrolled(camera: picamera.PiCamera) -> bytes:
    await trio.sleep(2)
    return await trio.to_thread.run_sync(_capture, camera)


async def _capture_regular(camera: picamera.PiCamera, led_panel_control) -> bytes:
    await led_panel_control({"blue": 75, "red": 75, "farRed": 0})
    await trio.sleep(4)
    return await trio.to_thread.run_sync(_capture, camera)


def _capture_np_unencoded(camera: picamera.PiCamera, resolution, format="rgb"):
    # Camera rounds up to nearest 32 horizontal pixels, and nearest 16 vertical.
    (x, y) = resolution
    x_orig = x
    y_orig = y
    if x % 32 != 0:
        x += 32 - x % 32
    if y % 16 != 0:
        y += 16 - y % 16
    buffer = np.empty((y * x * 3,), dtype=np.uint8)
    camera.capture(buffer, format)
    buffer = buffer.reshape((y, x, 3))
    return buffer[:y_orig, :x_orig, :]


async def _capture_nir(camera: picamera.PiCamera, led_panel_control) -> bytes:
    await led_panel_control({"blue": 0, "red": 0, "farRed": 75})
    await trio.sleep(4)
    nir_rgb = await trio.to_thread.run_sync(_capture_np_unencoded, camera, (1640, 1232))

    im = Image.fromarray(nir_rgb[:, :, 0])
    bytes_stream = io.BytesIO()
    im.save(bytes_stream, format="png")
    bytes_stream.seek(0)
    return bytes_stream.read()


async def _capture_ndvi(camera: picamera.PiCamera, led_panel_control) -> bytes:
    def process(red_rgb, nir_rgb) -> bytes:
        red_r = (red_rgb[:, :, 0]).astype(np.float)
        del red_rgb

        nir_r = (nir_rgb[:, :, 0]).astype(np.float)
        del nir_rgb

        ndvi = (nir_r - red_r) / (nir_r + red_r)
        del nir_r, red_r
        ndvi = ((ndvi - ndvi.min()) * (1 / (ndvi.max() - ndvi.min()) * 255)).astype(
            np.uint8
        )

        im = Image.fromarray(ndvi)
        bytes_stream = io.BytesIO()
        im.save(bytes_stream, format="png")  # Takes quite a lot of time.
        bytes_stream.seek(0)
        return bytes_stream.read()

    await led_panel_control({"blue": 0, "red": 75, "farRed": 0})
    await trio.sleep(4)
    red_rgb = await trio.to_thread.run_sync(_capture_np_unencoded, camera, (1640, 1232))

    await led_panel_control({"blue": 0, "red": 0, "farRed": 75})
    await trio.sleep(4)
    nir_rgb = await trio.to_thread.run_sync(_capture_np_unencoded, camera, (1640, 1232))

    return await trio.to_thread.run_sync(process, red_rgb, nir_rgb)


class PiCameraV2(Peripheral):
    COMMANDS = True

    def __init__(self, *args, configuration):
        super().__init__(*args)

        configuration = {"camera": "piCameraV2"}
        if configuration["camera"] == "piCameraV2":
            self.camera = picamera.PiCamera(resolution=(1640, 1232), sensor_mode=3)
        else:
            raise UnknownCamera()

    async def _do(self, command: Command):
        led_control_required = command in [Command.REGULAR, Command.NDVI, Command.NIR]
        led_panel_control = None
        if led_control_required:
            led_panel = _find_led_panel(self.manager.peripherals)
            if led_panel is not None:
                led_panel_control = self.manager.control(led_panel)

        if led_panel_control is None and command is not Command.UNCONTROLLED:
            raise Incompatable(
                "Could not find controllable LED panel, but control was required for requested command."
            )

        if led_control_required:
            async with led_panel_control as control:
                logger.debug("got LED panel control")
                led_panel_control.reset_on_exit = True

                if command is Command.REGULAR:
                    result = await _capture_regular(self.camera, control)
                elif command is Command.NIR:
                    result = await _capture_nir(self.camera, control)
                elif command is Command.NDVI:
                    result = await _capture_ndvi(self.camera, control)

                return PeripheralCommandResult(
                    media_type="image/png", data=result, metadata=None
                )
        else:
            if command is Command.UNCONTROLLED:
                result = await _capture_uncontrolled(self.camera)

            return PeripheralCommandResult(
                media_type="image/png", data=result, metadata=None
            )

    async def do(self, command):
        logger.debug(f"received command {command}")
        if command == "uncontrolled":
            return await self._do(Command.UNCONTROLLED)
        elif command == "regular":
            return await self._do(Command.REGULAR)
        elif command == "nir":
            return await self._do(Command.NIR)
        elif command == "ndvi":
            return await self._do(Command.NDVI)

    # async def run(self):
    #     await trio.sleep(2.0)
