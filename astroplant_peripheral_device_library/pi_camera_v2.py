"""
Implements the Raspberry Pi V2 camera.

For lighting-controlled pictures (Command.{REGULAR, NIR, NDVI}), this
implementation assumes availability of exactly one
astroplant_peripheral_device_library.led_panel.LedPanel. To take pictures, it
temporarily assumes exclusive control of the LED panel and sets lighting as
needed.
"""

import io
import logging
from typing import Iterable

import numpy as np
import picamera2
import schedule
import trio
from astroplant_kit.peripheral import Data, Peripheral, PeripheralCommandResult
from PIL import Image

from .led_panel import LedPanel

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


def _capture(camera: picamera2.Picamera2) -> bytes:
    """
    Capture an image to png.
    """
    bytes_stream = io.BytesIO()
    camera.capture_file(bytes_stream, format="png")
    bytes_stream.seek(0)
    return bytes_stream.read()


async def _capture_uncontrolled(camera: picamera2.Picamera2) -> bytes:
    await trio.sleep(2)
    return await trio.to_thread.run_sync(_capture, camera)


async def _capture_regular(camera: picamera2.Picamera2, led_panel_control) -> bytes:
    await led_panel_control({"blue": 75, "red": 75, "farRed": 0})
    await trio.sleep(4)
    return await trio.to_thread.run_sync(_capture, camera)


def _capture_np_unencoded(camera: picamera2.Picamera2, resolution, format="rgb"):
    # Camera rounds up to nearest 32 horizontal pixels, and nearest 16 vertical.
    (x, y) = resolution
    x_orig = x
    y_orig = y
    if x % 32 != 0:
        x += 32 - x % 32
    if y % 16 != 0:
        y += 16 - y % 16
    buffer = np.empty((y * x * 3,), dtype=np.uint8)
    camera.capture_file(buffer, format=format)
    buffer = buffer.reshape((y, x, 3))
    return buffer[:y_orig, :x_orig, :]


async def _capture_nir(camera: picamera2.Picamera2, led_panel_control) -> bytes:
    await led_panel_control({"blue": 0, "red": 0, "farRed": 75})
    await trio.sleep(4)
    nir_rgb = await trio.to_thread.run_sync(_capture_np_unencoded, camera, (1640, 1232))

    im = Image.fromarray(nir_rgb[:, :, 0])
    bytes_stream = io.BytesIO()
    im.save(bytes_stream, format="png")
    bytes_stream.seek(0)
    return bytes_stream.read()


async def _capture_ndvi(camera: picamera2.Picamera2, led_panel_control) -> bytes:
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
    RUNNABLE = True

    def __init__(self, *args, configuration):
        super().__init__(*args)

        self._nursery = None

        if configuration["camera"] == "piCameraV2":
            self.camera = picamera2.Picamera2()
            config = self.camera.create_still_configuration(main={"size": (1640, 1232)})
            self.camera.configure(config)
        else:
            raise UnknownCamera()

        self.schedule = configuration["schedule"]

    async def set_up(self):
        self.camera.start()

        self._scheduler = schedule.Scheduler()
        for task in self.schedule:
            self._scheduler.every().day.at(task["time"]).do(
                self._spawn_command, task["command"]
            )

    async def clean_up(self):
        self.camera.stop()

    def _spawn_command(self, command):
        self._nursery.start_soon(self._handle_command_with_control, command)

    async def _handle_command_with_control(self, command):
        logger.debug(f"Spawning {command}")
        cmd = Command.UNCONTROLLED
        if command == "uncontrolled":
            cmd = Command.UNCONTROLLED
        elif command == "regular":
            cmd = Command.REGULAR
        elif command == "nir":
            cmd = Command.NIR
        elif command == "ndvi":
            cmd = Command.NDVI

        # Block until nothing can call `do` anymore.
        async with self.manager.control(self):
            return await self._handle_command(cmd)

    async def _handle_command(self, command: Command):
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
                    file_name = "regular.png"
                elif command is Command.NIR:
                    result = await _capture_nir(self.camera, control)
                    file_name = "nir.png"
                elif command is Command.NDVI:
                    result = await _capture_ndvi(self.camera, control)
                    file_name = "ndvi.png"

                media = self.create_media(file_name, "image/png", result, None)
        else:
            if command is Command.UNCONTROLLED:
                result = await _capture_uncontrolled(self.camera)
                file_name = "uncontrolled.png"

            media = self.create_media(file_name, "image/png", result, None)

        if media is not None:
            await self._publish_data(Data(media))
            return media

    async def run(self):
        async with trio.open_nursery() as nursery:
            while True:
                self._nursery = nursery
                await trio.sleep(self._scheduler.idle_seconds)
                self._scheduler.run_pending()

    async def do(self, command):
        logger.debug(f"received command {command}")
        if command == "uncontrolled":
            media = await self._handle_command(Command.UNCONTROLLED)
        elif command == "regular":
            media = await self._handle_command(Command.REGULAR)
        elif command == "nir":
            media = await self._handle_command(Command.NIR)
        elif command == "ndvi":
            media = await self._handle_command(Command.NDVI)
        return PeripheralCommandResult(media=media)
