
# VDL Parkings

[![GitHub Release](https://img.shields.io/github/v/release/janreimen/HA-VDL-Parkings)](https://github.com/janreimen/HA-VDL-Parkings/releases)
[![License](https://img.shields.io/github/license/janreimen/HA-VDL-Parkings)](LICENSE)
[![HACS](https://img.shields.io/badge/HACS-Integration-41BDF5.svg)](https://hacs.xyz/)

A Home Assistant custom integration for monitoring public car parks in Luxembourg using the VDL (Ville de Luxembourg) parking API.

The integration provides live parking availability, occupancy information, parking status, Home Assistant zones and API diagnostics.

It supports individual parking selection and configurable day/night polling schedules.

---

## Features

- Monitor selected VDL car parks in Luxembourg.
- Display available, occupied and total parking spaces.
- Calculate and expose occupancy information.
- Monitor parking status:
  - Open
  - Full
  - Out of service
- Create and maintain Home Assistant zones for selected parking locations.
- Configure the monitored parkings through the integration options.
- Configure individual day/night polling schedules per parking.
- Monitor API connectivity and failures.
- Supports four interface languages:
  - Lëtzebuergesch
  - Deutsch
  - Français
  - English
- Includes a dedicated dashboard YAML example.
- Includes a reusable Lovelace custom card.

## Requirements

- Home Assistant.
- Internet connectivity to access the VDL parking API.
- HACS for the recommended installation method.

The integration uses Home Assistant's shared HTTP session.

## Installation

### Method 1: HACS

1. Open HACS in Home Assistant.
2. Select **Integrations**.
3. Open the three-dot menu.
4. Select **Custom repositories**.
5. Add:

   `https://github.com/janreimen/HA-VDL-Parkings`

6. Select **Integration** as the category.
7. Search for **VDL Parkings**.
8. Install the integration.
9. Restart Home Assistant.

If the repository becomes available in the official HACS catalogue, it can be installed directly without adding a custom repository.

### Method 2: Manual installation

1. Download or clone this repository.
2. Copy the `custom_components/vdl_parkings` directory into your Home Assistant configuration directory:

   ```text
   config/
   └── custom_components/
       └── vdl_parkings/
   ```

3. Restart Home Assistant.

## Initial configuration

After installation:

1. Open **Settings → Devices & services**.
2. Select **Add integration**.
3. Search for **VDL Parkings**.
4. Select the parkings you want to monitor.
5. Choose the integration language.
6. Complete the configuration.

The integration will retrieve the parking information from the VDL API.

At least one parking must be selected.

## Integration options

Open:

**Settings → Devices & services → VDL Parkings → Configure**

The options flow allows you to manage the selected parkings and their polling schedules.

### Parking selection

Select the parkings you want Home Assistant to monitor.

You can change this selection later without manually removing and recreating the integration.

### Language

The integration supports:

| Code | Language |
|---|---|
| `lu` | Lëtzebuergesch |
| `de` | Deutsch |
| `fr` | Français |
| `en` | English |

### Polling schedules

Each selected parking has its own schedule.

The schedule contains:

| Setting | Default | Description |
|---|---:|---|
| Day start | 06:00 | Start of the daytime schedule |
| Night start | 23:00 | Start of the nighttime schedule |
| High-frequency interval | 60 seconds | Refresh interval during the day |
| Low-frequency interval | 600 seconds | Refresh interval during the night |

The schedule determines which interval is applied to each parking.

The intervals can be configured individually for each selected parking.

### Important: API request behaviour

The VDL API currently returns all parking records in a single response.

The integration therefore uses a shared API request when one or more parking records are due for an update.

Individual parking schedules control when the corresponding records are refreshed and published in Home Assistant. They do not generate a separate upstream API request for every parking.

A scheduler checks for due parking records every 30 seconds.

---

## Entities

The integration creates sensors and binary sensors for the selected parkings.

Exact entity IDs depend on the parking name and Home Assistant entity ID generation.

### Sensors

| Sensor | Description |
|---|---|
| Total capacity | Total number of parking spaces |
| Available spaces | Number of currently available spaces |
| Occupied spaces | Number of occupied spaces |
| Occupancy rate | Percentage of occupied spaces |

### Binary sensors

| Binary sensor | Description |
|---|---|
| Open | Indicates whether the parking is open |
| Full | Indicates whether the parking is full |
| Out of service | Indicates whether the parking is out of service |
| API reachable | Indicates API connectivity |

### Parking attributes

Parking entities expose additional attributes where applicable:

| Attribute | Description |
|---|---|
| `parking_id` | VDL parking identifier |
| `parking_name` | Parking name |
| `last_updated` | Last update timestamp |

These attributes are also used by the custom Lovelace card to associate entities belonging to the same parking.

### API diagnostics

The integration also provides diagnostic information, including:

- Last successful API response.
- Number of consecutive API failures.
- API connectivity status.

These entities can be used in dashboards and automations.

---

## Home Assistant zones

The integration can create Home Assistant zones for the selected parkings using their location information.

Zones are maintained through the integration's parking-to-zone mapping.

When the selected parking configuration changes, zones associated with deselected parkings are removed.

**Note:** Check your existing zone configuration before changing parking selections if you have manually customized integration-created zones.

---

## Dashboard

The repository includes a dashboard example:

```text
dashboard/vdl_parkings.yaml
```

It provides:

- Parking overview.
- Available spaces.
- Occupancy visualization.
- Parking status.
- API diagnostics.

See:

[Dashboard installation and configuration](docs/DASHBOARD.md)

## Custom Lovelace card

The repository also includes a reusable JavaScript card:

```text
www/vdl-parkings-card.js
```

The card automatically discovers parking entities and displays:

- Parking name.
- Available spaces.
- Total capacity.
- Occupied spaces.
- Occupancy percentage.
- Open/full/out-of-service status.

### Installation

The JavaScript file must be copied manually to:

```text
/config/www/vdl-parkings-card.js
```

Register the following Lovelace resource:

| Setting | Value |
|---|---|
| URL | `/local/vdl-parkings-card.js` |
| Type | JavaScript Module |

Then add the card to a dashboard:

```yaml
type: custom:vdl-parkings-card
title: VDL Parkings
show_status: true
show_occupancy: true
```

To display only specific parking IDs:

```yaml
type: custom:vdl-parkings-card
title: Selected parkings
parking_ids:
  - "27"
  - "8"
show_status: true
show_occupancy: true
```

See [Dashboard documentation](docs/DASHBOARD.md) for full instructions.

---

## Example automations

### Notify when a parking has available spaces

Replace the example entity ID with the actual available-spaces sensor in your installation.

```yaml
automation:
  - alias: "VDL - Parking spaces available"
    description: "Notify when parking spaces become available."
    triggers:
      - trigger: numeric_state
        entity_id: sensor.example_parking_available_spaces
        above: 0
    actions:
      - action: notify.notify
        data:
          title: "Parking available"
          message: >
            There are now
            {{ states('sensor.example_parking_available_spaces') }}
            spaces available.
```

### Notify when a parking becomes full

```yaml
automation:
  - alias: "VDL - Parking full"
    description: "Notify when a parking becomes full."
    triggers:
      - trigger: state
        entity_id: binary_sensor.example_parking_full
        to: "on"
    actions:
      - action: notify.notify
        data:
          title: "Parking full"
          message: "The selected VDL parking is now full."
```

These are examples. Adapt the entity IDs and notification service to your installation.

---

## Troubleshooting

### Integration cannot connect

Check:

- Home Assistant has internet connectivity.
- The VDL API is reachable.
- The Home Assistant logs for integration errors.

### No parking data appears

Check:

- At least one parking is selected.
- The initial API request succeeded.
- The parking entities are enabled.
- The API diagnostic entities do not report repeated failures.

### Configure button returns an error

Make sure that you are running the matching integration files from the same release.

If the options flow fails, check the Home Assistant logs for a Python traceback and verify that the options flow does not assign to the read-only `config_entry` property.

### Polling does not match the configured interval

Remember:

- The scheduler checks every 30 seconds.
- The configured interval is evaluated per parking.
- One API response may contain multiple parking records.
- Only parking records due for refresh are updated.

### Dashboard card is not recognized

Check:

- The JavaScript file is installed in `/config/www/`.
- The Lovelace resource is registered.
- The resource type is JavaScript Module.
- The browser cache has been refreshed.

### The card displays no parkings

Check that the available-spaces sensors expose the `parking_id` attribute.

Also verify that the selected parking IDs in the card configuration match the IDs exposed by the integration.

---

## Diagnostics

When reporting an issue, include:

1. Home Assistant version.
2. VDL Parkings integration version.
3. Relevant Home Assistant log entries.
4. Integration diagnostics downloaded through Home Assistant.

Diagnostics are designed to provide configuration and coordinator information without including parking coordinates.

Please review diagnostic output before sharing it publicly.

---

## Development

Repository:

https://github.com/janreimen/HA-VDL-Parkings

Main integration directory:

```text
custom_components/vdl_parkings/
```

Relevant files:

| File | Purpose |
|---|---|
| `__init__.py` | Integration setup, unload and migration |
| `config_flow.py` | Initial setup and options |
| `const.py` | Constants and configuration helpers |
| `coordinator.py` | API coordination and polling scheduler |
| `sensor.py` | Parking and API sensors |
| `binary_sensor.py` | Parking status and API binary sensors |
| `zone.py` | Home Assistant zone management |
| `diagnostics.py` | Diagnostic information |
| `manifest.json` | Integration metadata |
| `translations/` | Supported UI translations |

Dashboard files:

```text
dashboard/
docs/
www/
```

### Development guidelines

- Keep entity unique IDs stable.
- Preserve existing configuration during migrations.
- Use Home Assistant's shared HTTP session.
- Avoid unnecessary API requests.
- Keep per-parking schedule behaviour independent.
- Keep translations synchronized.
- Update the changelog and release notes for each release.

---

## Version

Current target release: **0.1.4**

See [CHANGELOG.md](CHANGELOG.md) for release history and [GitHub Releases](https://github.com/janreimen/HA-VDL-Parkings/releases) for published releases.

## Support

For bug reports, feature requests and questions:

[Open an issue](https://github.com/janreimen/HA-VDL-Parkings/issues)

## License

See the [LICENSE](LICENSE) file.

