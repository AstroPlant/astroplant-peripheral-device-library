# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0b8] - 2022-09-09

### Fix

- DHT22: wait for measurement (regression introduced in 1.0.0b7)

## [1.0.0b7] - 2022-09-08

### Changed

- Target Raspbian OS Bullseye
- As Bullseye is now targeted, move from legacy camera stack to libcamera using picamera2

### Fix

- LCD: improve exception handling

### Added

- This changelog

## [1.0.0b6] - 2022-09-07

### Added

- Add set up and clean up handlers for most peripherals
- Explicitly re-raise some expected exceptions as `PeripheralException`

### Fixed

- Fix pigpio resource leak for peripherals using duty cycles and I2C
- Let MH-Z19 CO2 sensor actually use the `serialFile` configuration option

### Changed

- Simplify some threading behavior
- Move some blocking I/O to dedicated threads
