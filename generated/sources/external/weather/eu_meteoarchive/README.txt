MeteoArchive Historical API - bulk export (daily aggregation, reanalysis + station blend)
Query: /v1/archive?latitude=..&longitude=..&daily=...&timezone=auto  (v2 endpoint from 2026-03-01)
One JSON per location and request window. Values are model grid-cell values (see 'elevation'), not station observations.
API v2 changelog (2026-03-01): variable names now snake_case with underscores between words
(weathercode -> weather_code, windspeed_10m_max -> wind_speed_10m_max, ...); wind speed default unit is now m/s;
new variables temperature_2m_mean, precipitation_hours, sunshine_duration (seconds).
weather code: WMO 4677 interpretation codes (0 clear .. 99 thunderstorm with hail).
Data for the last 1-2 days may be missing (ERA5T latency).
