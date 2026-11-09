# Zone management

## Purpose

VDL Parkings can create Home Assistant zones for configured parking facilities.

These zones provide geographic representations of parking locations and can be used by Home Assistant features that support zones.

## Zone properties

Zones created by the integration use the following characteristics:

| Property | Value |
|---|---|
| Name | `Parking <parking name>` |
| Coordinates | Coordinates supplied by the VDL data |
| Radius | 100 metres |
| Icon | `mdi:parking` |

The coordinates are derived from the parking facility's location data.

## Zone tracking

Home Assistant zones are global objects. They are not private entities owned exclusively by the VDL Parkings integration.

The integration therefore keeps track of the zones it manages using its configuration entry data.

This allows the integration to identify its own zones when updating or cleaning up its configuration.

## Creation and updates

When the integration processes a configured parking facility:

1. It checks whether a corresponding managed zone already exists.
2. It compares the stored location with the current parking coordinates.
3. If the location has changed, the old managed zone is removed and the zone is recreated or an appropriate matching zone is reused.
4. If no corresponding zone exists, a new zone is created.

The zone name follows the parking facility name supplied by the VDL data.

## Unloading and removal

**Important:** Home Assistant zones are global objects.

When the integration unloads, it removes the zones tracked as managed by its configuration entry.

This means that zones created by the integration may also disappear from Home Assistant when the integration is unloaded or removed.

Do not manually reuse an integration-managed zone for an unrelated purpose unless you understand this lifecycle behaviour.

## Limitations

- Zones depend on valid coordinates from the VDL data.
- A change in the upstream parking location data can cause a zone to be recreated.
- Zones are global Home Assistant objects, not private integration entities.
- Other integrations or automations may reference these zones.

## Troubleshooting

If a parking zone is missing or has an unexpected location:

1. Check whether the parking facility provides valid coordinates in the VDL data.
2. Check the Home Assistant logs for zone-related errors.
3. Check the configured parking facilities.
4. Verify that the zone has not been manually changed or removed.

For general integration support, see [SUPPORT.md](../SUPPORT.md).
