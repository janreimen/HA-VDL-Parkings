
# VDL Parkings 0.1.4

This release focuses on improving configuration, parking-specific update schedules, diagnostics and dashboard usability.

VDL Parkings now provides more control over which car parks are monitored and how frequently their information is refreshed.

## Highlights

### Individual parking configuration

You can select the VDL car parks you want to monitor through the integration configuration.

The selection can be changed later through the integration options without manually reinstalling the integration.

### Day/night polling schedules

Each selected parking can have its own polling schedule.

Configure:

- Daytime start.
- Nighttime start.
- High-frequency update interval.
- Low-frequency update interval.

Example default configuration:

| Setting | Value |
|---|---:|
| Day starts | 06:00 |
| Night starts | 23:00 |
| Day interval | 60 seconds |
| Night interval | 600 seconds |

The scheduler checks for due parking records every 30 seconds.

### More API diagnostics

Additional diagnostic information helps identify connectivity and API update problems.

The integration exposes:

- API reachability.
- Last successful API response.
- Consecutive API failures.

### Four interface languages

The integration includes translations for:

- Lëtzebuergesch
- Deutsch
- Français
- English

### Dashboard and custom Lovelace card

Version 0.1.4 introduces two dashboard options:

1. A dedicated Home Assistant dashboard example.
2. A reusable Lovelace custom card.

The card displays:

- Parking name.
- Available spaces.
- Total capacity.
- Occupied spaces.
- Occupancy percentage.
- Open, full and out-of-service status.

See [docs/DASHBOARD.md](docs/DASHBOARD.md) for installation instructions.

**Note:** The custom card must currently be copied manually into `/config/www/` and registered as a JavaScript Module resource.

## API behaviour

The VDL API currently returns all parking records in one response.

The integration uses a shared API request whenever one or more parking records are due for refresh.

Individual schedules determine when each parking record is refreshed in Home Assistant. They do not generate separate API requests for each parking.

## Upgrade

1. Update the integration files through HACS or your manual installation method.
2. Restart Home Assistant.
3. Open **Settings → Devices & services → VDL Parkings**.
4. Review the selected parkings and polling schedules.
5. Check the API diagnostic entities.
6. Install or update the custom Lovelace card if you use it.

Existing configuration should be preserved by the integration migration.

## Compatibility

- Home Assistant minimum version: 2026.3.0
- Integration domain: `vdl_parkings`
- Release: `0.1.4`

## Important testing notice

This release description documents the intended 0.1.4 functionality. The release should only be published after testing configuration setup, migration, polling, API failure recovery, zone handling and dashboard rendering on the target Home Assistant installation.

## Links

- [Repository](https://github.com/janreimen/HA-VDL-Parkings)
- [Issues](https://github.com/janreimen/HA-VDL-Parkings/issues)
- [Dashboard documentation](docs/DASHBOARD.md)
- [Changelog](CHANGELOG.md)

