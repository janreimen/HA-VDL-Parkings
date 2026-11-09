# Version 0.1.1 development implementation

## Included in this development patch

- Selectable parking IDs retained in config entry data and editable in Options.
- Per-parking high/low polling intervals and day/night boundaries.
- One shared VDL HTTP request updates only parking records whose own timer is due.
- API health entities: reachability, last successful response, consecutive failures and last error attributes.
- Four language files: Luxembourgish, German, French and English.
- Starter Lovelace dashboard with history and statistics graphs.

## Important implementation notes

The VDL endpoint currently returns a full parking list in one HTTP response. Per-parking schedules therefore govern when an individual parking record is refreshed in Home Assistant; they do not create separate HTTP requests per parking. A single shared request is made whenever one or more selected parkings become due.

Home Assistant's `statistics-graph` can show long-term mean/min/max statistics when Recorder and supported long-term statistics are available. The included dashboard does not claim to provide a mathematical regression line. A true regression trendline can be added with ApexCharts Card as an optional frontend dependency.

## Review items before merging

- Run Ruff/Black and Home Assistant integration tests against the minimum supported Home Assistant release.
- Verify VDL JSON response shape and numeric/null handling against a live response.
- Test Options flow selection changes, including adding/removing parking IDs and reloading the entry.
- Confirm entity IDs in the dashboard against the actual entity registry; Home Assistant may slugify names differently.
- Verify the `statistics-graph` entities expose long-term statistics in the target Home Assistant version.
- Verify options form fields for each parking are presented as intended in the frontend.
