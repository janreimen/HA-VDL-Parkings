# Data source

## Upstream service

The integration retrieves public parking information from the Ville de Luxembourg (VDL) website.

Endpoint:

`https://www.vdl.lu/fr/parking/data.json`

The endpoint is accessed over HTTPS using an asynchronous HTTP client.

## Update interval

The integration polls the endpoint every 60 seconds.

The interval controls how frequently Home Assistant requests data. It does not guarantee that the upstream service publishes new information at the same frequency.

## Data fields

The integration uses the following information from the parking data:

| Field | Purpose |
|---|---|
| `total` | Total parking capacity |
| `actuel` | Currently available spaces |
| `ouvert` | Parking open/closed status |
| `complet` | Parking full status |
| `panne` | Out-of-service or fault status |
| `coords` | Geographic coordinates used for location information |

The exact structure and meaning of these fields are controlled by the upstream VDL service.

## Derived values

The integration derives additional values from the upstream data.

### Occupied spaces

Occupied spaces are calculated as:

`max(total - available, 0)`

This prevents a negative occupied-space value if the upstream data contains inconsistent values.

### Occupancy rate

The occupancy rate is calculated from occupied spaces and total capacity.

When total capacity is zero, the integration returns an occupancy rate of zero to avoid division by zero.

The resulting percentage is rounded.

## Data quality and limitations

The integration depends on the availability and stability of the VDL endpoint.

Potential issues include:

- Temporary network or service outages
- Missing or invalid fields
- Changes to the upstream JSON structure
- Delayed updates from the parking operators
- Inconsistent values supplied by the upstream service

The integration cannot independently verify whether the reported number of available spaces matches the physical situation.

## Troubleshooting

If parking data is unavailable or appears incorrect:

1. Check whether the VDL website is reachable.
2. Check the Home Assistant logs for integration errors.
3. Verify that the parking facility is still present in the upstream data.
4. Check whether the upstream response structure has changed.

For user support, see [SUPPORT.md](../SUPPORT.md).
