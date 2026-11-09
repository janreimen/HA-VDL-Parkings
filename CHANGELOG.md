# Changelog

All notable changes to VDL Parkings are documented in this file.

The integration version is defined in `custom_components/vdl_parkings/manifest.json`.

## [Unreleased]

### Documentation
- Reworked the README to describe the current integration and its features.
- Added architecture, data source, entity reference and zone management documentation.
- Added contribution guidelines, support information and project policies.

### Fixed
- Updated zone storage access for compatibility with the Home Assistant zone data structure.

## [0.1.0]

Initial documented integration version.

### Added
- UI-based selection of public parking locations in Luxembourg City.
- Automatic polling of the VDL public parking data endpoint every 60 seconds.
- Available spaces, total capacity, occupied spaces and occupancy rate sensors.
- Open, full and out-of-service binary sensors.
- Automatic creation and management of Home Assistant parking zones.
- Device grouping for each selected parking location.
- English and French translations.
