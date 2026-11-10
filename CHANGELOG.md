
# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project aims to follow [Semantic Versioning](https://semver.org/).

## [0.1.4] - 2026-11-10

### Added

- Per-parking selection management through the integration options.
- Individual polling schedules for each selected parking.
- Configurable daytime and nighttime start times.
- Configurable high-frequency and low-frequency polling intervals.
- A scheduler that checks for parking records due for refresh.
- API connectivity and failure diagnostics.
- Additional parking entity attributes:
  - `parking_id`
  - `parking_name`
  - `last_updated`
- Luxembourgish, German, French and English translations.
- Dedicated Lovelace dashboard YAML example.
- Reusable VDL Parkings custom Lovelace card.
- Dashboard installation and configuration documentation.
- Expanded integration and development documentation.

### Changed

- Replaced the fixed polling interval with a per-parking day/night scheduling mechanism.
- Reused Home Assistant's shared aiohttp session for VDL API requests.
- Improved configuration and options-flow handling.
- Improved configuration migration and preservation of existing settings.
- Updated integration metadata and version information.
- Improved coordinator diagnostics and error reporting.

### Fixed

- Addressed the options-flow implementation issue involving the read-only `config_entry` property.
- Improved handling of selected parking IDs and their schedules.
- Improved handling of missing parking records returned by the VDL API.
- Improved association of parking entities for dashboard discovery.

### Technical notes

- The VDL API currently returns all parking records in a single response.
- The integration performs a shared API request when one or more selected parking records are due for an update.
- Per-parking schedules control when individual parking records are refreshed and published in Home Assistant; they do not trigger separate API requests for every parking.
- The scheduler checks for due records every 30 seconds.
- The custom Lovelace card is distributed in the repository under `www/` and must currently be copied manually to `/config/www/`.
- Existing entity unique IDs should be preserved during upgrades.

### Validation status

This changelog describes the 0.1.4 implementation scope. It does not imply that all functionality has already been tested against a live Home Assistant installation.

Before publishing, validate:

- Initial integration setup.
- Options flow and configuration persistence.
- Migration from existing configuration entries.
- Day/night polling transitions.
- Parking selection changes.
- API failures and recovery.
- Zone creation and cleanup.
- Sensor and binary sensor entity attributes.
- Dashboard and custom Lovelace card rendering.

---

## [0.1.3] - Previous baseline

- Previous main-branch baseline.
- Parking data initialization and zone creation improvements.

[0.1.4]: https://github.com/janreimen/HA-VDL-Parkings/compare/0.1.3...0.1.4
[0.1.3]: https://github.com/janreimen/HA-VDL-Parkings/releases/tag/0.1.3

