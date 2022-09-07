# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

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
