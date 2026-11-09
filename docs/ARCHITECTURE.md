# Architecture

## Overview

VDL Parkings is a Home Assistant custom integration that retrieves parking availability data from the Ville de Luxembourg (VDL) public parking data service.

The integration uses cloud polling. It periodically retrieves the parking data, processes the response and exposes the results as Home Assistant entities.

## Main components

The integration is located in:

`custom_components/vdl_parkings/`

Its main responsibilities are divided into the following areas:

- **Configuration flow** – lets the user select the parking facilities to monitor.
- **Data coordinator** – retrieves and refreshes data from the VDL endpoint.
- **Data processing** – converts the API response into values suitable for Home Assistant.
- **Sensor platform** – creates numerical parking entities.
- **Binary sensor platform** – creates parking status entities.
- **Zone management** – creates and maintains corresponding Home Assistant zones.
- **Translations** – provides user-facing strings in supported languages.

## Data flow

1. Home Assistant loads the integration.
2. The configuration flow allows the user to select parking facilities.
3. The integration creates its data coordinator.
4. The coordinator retrieves the current parking data from the VDL service.
5. The response is matched against the configured parking facilities.
6. The integration processes availability and status information.
7. Sensor and binary sensor entities expose the resulting values.
8. The coordinator repeats the data retrieval periodically.

## Polling

The integration uses a polling interval of 60 seconds.

This is the configured refresh interval, not a guarantee that the upstream data itself is updated every 60 seconds. Actual data freshness depends on the VDL service.

## Entity platforms

The integration provides two platforms:

### Sensor

Numerical information for each configured parking facility:

- Available spaces
- Total capacity
- Occupied spaces
- Occupancy rate

### Binary sensor

Status information for each configured parking facility:

- Open
- Full
- Out of service

The out-of-service entity is intended as diagnostic/status information.

## Error handling

The integration depends on an external HTTP service. Network failures, invalid responses or changes to the upstream data structure can prevent a successful refresh.

A failed refresh should not be interpreted as a parking facility being closed or full. The availability of current data depends on a successful update.

## Home Assistant zones

The integration can create Home Assistant zones for configured parking facilities.

Zone objects are global Home Assistant objects rather than private entities belonging exclusively to this integration. The integration tracks the zones it manages through its configuration entry data.

See [Zone management](ZONE_MANAGEMENT.md) for details and lifecycle considerations.
