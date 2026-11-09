# VDL Parkings – Home Assistant Integration

A custom integration for [Home Assistant](https://www.home-assistant.io/) that monitors public parking availability in Luxembourg City using data published by [Ville de Luxembourg (VDL)](https://www.vdl.lu/).

Select the car parks you want to monitor and Home Assistant will automatically create sensors, binary sensors and map zones for them.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=janreimen&repository=HA-VDL-Parkings&category=integration)

---

## Features

- **Live parking information** from the public VDL parking data service.
- **Configurable parking selection** – choose which car parks to monitor during setup.
- **Automatic polling** every 60 seconds.
- **Parking sensors** for capacity, available spaces, occupied spaces and occupancy rate.
- **Parking status sensors** indicating whether a car park is open, full or out of service.
- **Automatic map zones** – creates a Home Assistant zone for each selected parking location.
- **Automatic zone management** – reuses existing matching zones, updates zones when coordinates change and removes zones associated with the integration when it is unloaded.
- **UI-based configuration** – no YAML configuration or API credentials required.
- **Device grouping** – entities belonging to a parking location are grouped under one Home Assistant device.

## Requirements

| Requirement | Version / Details |
|---|---|
| Home Assistant Core | 2026.3.0 or newer |
| Internet connection | Required |
| VDL account | Not required |
| API key | Not required |
| Configuration | Home Assistant UI |
| Update interval | 60 seconds |

The integration uses Home Assistant's `cloud_polling` model and retrieves information from the public VDL parking data endpoint.

## Installation

### HACS (recommended)

1. Open **HACS** in Home Assistant.
2. Open the three-dot menu and select **Custom repositories**.
3. Add the following repository:

   `https://github.com/janreimen/HA-VDL-Parkings`

4. Select **Integration** as the repository category.
5. Search for **VDL Parkings** and install it.
6. Restart Home Assistant.

Alternatively, use the button below:

[![Open VDL Parkings in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=janreimen&repository=HA-VDL-Parkings&category=integration)

### Manual installation

1. Download or clone this repository.
2. Copy the `custom_components/vdl_parkings` directory into your Home Assistant configuration directory.
3. Verify that the resulting directory structure is:

   ```text
   config/
   └── custom_components/
       └── vdl_parkings/
           ├── __init__.py
           ├── api.py
           ├── binary_sensor.py
           ├── config_flow.py
           ├── const.py
           ├── coordinator.py
           ├── manifest.json
           ├── sensor.py
           ├── zone.py
           └── translations/
   ```

4. Restart Home Assistant.

## Configuration

The integration is configured entirely through the Home Assistant UI.

1. Navigate to **Settings → Devices & Services**.
2. Select **Add Integration**.
3. Search for **VDL Parkings**.
4. Select the car parks you want to monitor.
5. Submit the configuration.

The integration retrieves the current list of public VDL car parks and presents them as a selectable list.

Only the selected locations are added to Home Assistant.

No username, password, API key or additional configuration is required.

## Entities

For every selected parking location, the integration creates four sensor entities and three binary sensor entities.

All entities are grouped under a Home Assistant device representing the corresponding parking location.

### Sensors

| Sensor | Description | Example value |
|---|---|---:|
| Available spaces | Number of currently available parking spaces | 125 |
| Total capacity | Total number of parking spaces | 500 |
| Occupied spaces | Calculated number of occupied spaces | 375 |
| Occupancy rate | Percentage of occupied spaces | 75% |

The occupancy rate is calculated as:

```text
Occupancy rate = Occupied spaces / Total capacity × 100
```

Occupied spaces are calculated as:

```text
Occupied spaces = Total capacity - Available spaces
```

The occupancy rate is rounded to the nearest whole percentage.

### Binary sensors

| Sensor | Description | On means |
|---|---|---|
| Open | Indicates whether the parking is open | Parking is open |
| Full | Indicates whether the parking is full | Parking is full |
| Out of service | Indicates whether the parking is unavailable due to a fault or service issue | Parking is out of service |

The `Out of service` entity is classified as a diagnostic entity in Home Assistant.

### Entity IDs

Home Assistant generates entity IDs based on the parking name and the configured language.

For example, a parking location named `Royal Hamilius` may produce entities such as:

```text
sensor.royal_hamilius_available_spaces
sensor.royal_hamilius_total_capacity
sensor.royal_hamilius_occupied_spaces
sensor.royal_hamilius_occupancy_rate

binary_sensor.royal_hamilius_open
binary_sensor.royal_hamilius_full
binary_sensor.royal_hamilius_out_of_service
```

The exact IDs may differ depending on Home Assistant's entity registry and naming conventions.

## Automatic parking zones

The integration automatically creates a Home Assistant zone for each selected parking location.

These zones use the geographical coordinates supplied by the VDL data service.

Each zone is created with:

| Property | Value |
|---|---|
| Name | `Parking <parking name>` |
| Latitude | VDL parking coordinates |
| Longitude | VDL parking coordinates |
| Radius | 100 metres |
| Icon | `mdi:parking` |

### Zone management

The integration maintains a mapping between selected parking IDs and their corresponding Home Assistant zone IDs.

This mapping prevents duplicate zones and allows the integration to manage its zones across reloads and configuration changes.

The zone management logic:

- Reuses an existing tracked zone if its coordinates still match.
- Updates the zone if the parking coordinates change.
- Looks for an existing parking zone at the same coordinates before creating a new one.
- Removes zones for parking locations that are no longer selected.
- Removes tracked zones when the integration is unloaded.

**Note:** Zones are Home Assistant global zones, not sensor entities. They can be used by the standard Home Assistant map, proximity integrations and automations.

If you manually delete a zone, the integration can recreate it during a subsequent setup.

## Example usage

### 1. Parking availability card

A simple Lovelace Entities card showing the current parking situation:

```yaml
type: entities
title: Royal Hamilius
entities:
  - entity: sensor.royal_hamilius_available_spaces
    name: Available spaces
  - entity: sensor.royal_hamilius_total_capacity
    name: Total capacity
  - entity: sensor.royal_hamilius_occupied_spaces
    name: Occupied spaces
  - entity: sensor.royal_hamilius_occupancy_rate
    name: Occupancy rate
  - entity: binary_sensor.royal_hamilius_open
    name: Open
  - entity: binary_sensor.royal_hamilius_full
    name: Full
```

### 2. Notify when parking spaces become available

Example automation that sends a notification when more than ten parking spaces are available and the parking is open:

```yaml
alias: Notify when parking has space
description: Notify when Royal Hamilius has more than 10 available spaces.
triggers:
  - trigger: numeric_state
    entity_id: sensor.royal_hamilius_available_spaces
    above: 10
conditions:
  - condition: state
    entity_id: binary_sensor.royal_hamilius_open
    state: "on"
actions:
  - action: notify.mobile_app_my_phone
    data:
      message: >
        Royal Hamilius has more than 10 available parking spaces.
mode: single
```

Replace `notify.mobile_app_my_phone` with your own notification service.

### 3. Display parking locations on a map

Once the integration has created the parking zones, they can be displayed using the standard Home Assistant Map card.

```yaml
type: map
entities:
  - zone.parking_royal_hamilius
  - zone.parking_gare
  - zone.parking_theatre
```

Replace the example zone entity IDs with the actual IDs created in your Home Assistant instance.

### 4. Use parking availability in templates

Example template sensor showing the number of free parking spaces:

```yaml
template:
  - sensor:
      - name: "Royal Hamilius Free Parking Spaces"
        unique_id: royal_hamilius_free_parking_spaces
        unit_of_measurement: "spaces"
        state: >
          {{ states('sensor.royal_hamilius_available_spaces') | int(0) }}
```

## Data
