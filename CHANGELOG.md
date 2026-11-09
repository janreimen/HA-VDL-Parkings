# Changelog

## 0.1.1 (development)

### Added
- Per-parking selection management through integration options.
- Per-parking day/night polling schedules.
- API connectivity and failure diagnostics.
- Luxembourgish, German, French and English translations.
- Starter Lovelace dashboard with history and long-term statistics graphs.

### Changed
- Replaced the fixed 60-second refresh with a 30-second scheduler that refreshes each selected parking according to its own configured high/low interval.
- Reused Home Assistant's shared aiohttp session for VDL API requests.

### Notes
- VDL currently provides all parking records in one response; per-parking schedules control record refresh/publication, not separate upstream API calls.
- This is a development build and requires testing against the target Home Assistant version.
