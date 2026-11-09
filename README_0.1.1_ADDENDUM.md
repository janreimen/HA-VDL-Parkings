# VDL Parkings 0.1.1 – development addendum

## New configuration

Open **Settings → Devices & services → VDL Parkings → Configure** to change monitored parkings, language and per-parking polling parameters.

Polling defaults:
- High-frequency window: 06:00–23:00
- High interval: 60 seconds
- Low interval: 600 seconds
- Minimum accepted high interval: 30 seconds
- Minimum accepted low interval: 60 seconds

Intervals are in seconds. The integration uses Home Assistant's local timezone.

## Dashboard

Import `dashboards/vdl_parkings.yaml` as a Lovelace dashboard. Replace example entity IDs with the IDs shown in **Developer Tools → States** if your entity registry uses different slugs.

## Statistics

Enable Home Assistant Recorder. Long-term graphs depend on Home Assistant statistics being available. Occupancy rate is a measurement sensor; check its statistics metadata after installation.

## API diagnostics

The API device exposes:
- API reachable
- Last successful API response
- Consecutive API failures
- Last error as an attribute
