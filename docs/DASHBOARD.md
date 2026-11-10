
# VDL Parkings – Dashboard and Lovelace Card

The VDL Parkings integration provides two dashboard options:

1. A dedicated Home Assistant dashboard.
2. A reusable Lovelace custom card that can be added to any existing dashboard.

Both options use the parking entities created by the integration.

## 1. Requirements

Before installing the dashboard, make sure that:

- The VDL Parkings integration is installed and configured.
- At least one parking is selected in the integration options.
- The integration has completed its first successful API update.
- The parking sensor and binary sensor entities are available.

The custom card uses the `parking_id` entity attribute to associate entities belonging to the same parking.

## 2. Install the custom Lovelace card

The JavaScript file is located in the repository:

```text
www/vdl-parkings-card.js
```

Home Assistant does not automatically install files from this repository directory.

### Manual installation

Copy the file to your Home Assistant configuration directory:

```text
/config/www/vdl-parkings-card.js
```

For example, using SSH:

```bash
mkdir -p /config/www
cp vdl-parkings-card.js /config/www/vdl-parkings-card.js
```

The source file must first be transferred from the repository to your Home Assistant system.

### Register the resource

In Home Assistant:

1. Open **Settings**.
2. Open **Dashboards**.
3. Select the dashboard menu.
4. Open **Resources**.
5. Add a new resource.

Use these settings:

| Setting | Value |
|---|---|
| URL | `/local/vdl-parkings-card.js` |
| Resource type | JavaScript Module |

Save the resource and reload the Home Assistant frontend.

If the card is not recognized, clear the browser cache and reload Home Assistant.

## 3. Use the custom card

Add a manual card to any dashboard.

Minimal configuration:

```yaml
type: custom:vdl-parkings-card
```

Full configuration:

```yaml
type: custom:vdl-parkings-card
title: VDL Parkings
show_status: true
show_occupancy: true
```

### Configuration options

| Option | Type | Default | Description |
|---|---|---|---|
| `type` | string | Required | `custom:vdl-parkings-card` |
| `title` | string | `VDL Parkings` | Card heading |
| `show_status` | boolean | `true` | Show open, full and out-of-service states |
| `show_occupancy` | boolean | `true` | Show occupancy percentage and progress bar |
| `parking_ids` | list | `[]` | Optional list of parking IDs to display |

### Display selected parkings only

Use the parking IDs returned by the VDL integration.

Example:

```yaml
type: custom:vdl-parkings-card
title: Selected parkings
parking_ids:
  - "27"
  - "8"
show_status: true
show_occupancy: true
```

An empty `parking_ids` list means that all discovered parking entities are displayed.

## 4. Dedicated dashboard

The repository contains a ready-to-import dashboard YAML file:

```text
dashboard/vdl_parkings.yaml
```

The dashboard includes:

- Parking overview.
- Available spaces and capacity.
- Occupancy visualization.
- Parking status indicators.
- API diagnostics.

### Import

1. Make sure the custom Lovelace card is installed and registered.
2. Open **Settings → Dashboards**.
3. Add a dashboard using the YAML configuration option available in your Home Assistant version.
4. Copy the contents of `dashboard/vdl_parkings.yaml`.
5. Save and open the dashboard.

If your Home Assistant installation uses YAML dashboard configuration, add the dashboard through your existing Lovelace configuration instead.

## 5. Entity discovery

The custom card discovers parking entities automatically.

It looks for available-space sensors with:

- Entity domain: `sensor`
- Entity ID suffix: `_available_spaces`
- Attribute: `parking_id`

It then searches for the corresponding entities using the same `parking_id`.

Expected entity types:

| Entity | Purpose |
|---|---|
| Available spaces | Number of currently available parking spaces |
| Total capacity | Total number of parking spaces |
| Occupied spaces | Number of occupied spaces |
| Occupancy rate | Occupancy percentage |
| Open | Parking is open |
| Full | Parking is full |
| Out of service | Parking is out of service |

The card uses the entity state values supplied by Home Assistant. It does not make additional requests to the VDL API.

## 6. API polling behaviour

The VDL API currently provides all parking records in one response.

The integration uses a shared API request and applies individual schedules to the selected parking records.

The schedules determine when each parking record is refreshed in Home Assistant. They do not create a separate upstream API request for every parking.

The dashboard displays the latest values available in Home Assistant.

## 7. Troubleshooting

### Custom card not found

Check that:

- The JavaScript file exists in `/config/www/`.
- The resource URL is `/local/vdl-parkings-card.js`.
- The resource type is JavaScript Module.
- The browser cache has been refreshed.

### No parking entities found

Check that:

- The integration is loaded.
- At least one parking is selected.
- The initial VDL API update succeeded.
- Available-space sensors have a `parking_id` attribute.

### Parking status is missing

Check that the binary sensors are enabled and available.

The card expects the binary sensor entities to have the following suffixes:

- `_open`
- `_full`
- `_out_of_service`

### Occupancy is not displayed

Check that the occupancy sensor is available and returns a numeric percentage.

### API diagnostics

The integration provides diagnostic entities for:

- Last successful API response.
- Consecutive API failures.

These can help identify API connectivity problems.

## 8. Development

The card is plain JavaScript and does not require a build process.

Source:

```text
www/vdl-parkings-card.js
```

When modifying the card:

1. Update the source file.
2. Test it in Home Assistant.
3. Reload the frontend.
4. Update the version and release notes when publishing a new release.

## 9. Limitations

- The card requires the parking entities and their `parking_id` attributes.
- The card does not retrieve data directly from VDL.
- Dashboard YAML may need minor adjustments depending on the Home Assistant dashboard configuration.
- The JavaScript card is manually installed unless a separate distribution mechanism is provided.

