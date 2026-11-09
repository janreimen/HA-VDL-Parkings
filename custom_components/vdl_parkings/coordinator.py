"""Per-parking polling coordinator and API health tracking."""

from datetime import datetime, time, timedelta
import logging

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import VdlParkingApi
from .const import (
    CONF_HIGH_INTERVAL, CONF_LOW_INTERVAL, CONF_PARKINGS, CONF_PARKING_SCHEDULES,
    CONF_DAY_START, CONF_NIGHT_START, DEFAULT_HIGH_INTERVAL, DEFAULT_LOW_INTERVAL,
    DEFAULT_DAY_START, DEFAULT_NIGHT_START, DOMAIN, SCHEDULER_TICK_SECONDS,
)

_LOGGER = logging.getLogger(__name__)


def _clock(value, fallback):
    """Parse HH:MM safely."""
    try:
        hour, minute = (int(part) for part in value.split(":"))
        return time(hour, minute)
    except (AttributeError, TypeError, ValueError):
        return time.fromisoformat(fallback)


class VdlParkingCoordinator(DataUpdateCoordinator):
    """Fetch the shared VDL feed only when at least one selected parking is due."""

    def __init__(self, hass, entry):
        self.entry = entry
        self.api = VdlParkingApi(async_get_clientsession(hass))
        self.selected = set(entry.data.get(CONF_PARKINGS, []))
        self.schedules = entry.options.get(CONF_PARKING_SCHEDULES, {})
        self.last_success = None
        self.last_attempt = None
        self.last_error = None
        self.consecutive_failures = 0
        self.api_reachable = False
        self._next_due = {parking_id: datetime.min.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE)
                          for parking_id in self.selected}
        super().__init__(
            hass, _LOGGER, name=DOMAIN,
            update_interval=timedelta(seconds=SCHEDULER_TICK_SECONDS),
        )
        # DataUpdateCoordinator initializes ``data`` itself; seed an empty
        # mapping after super() so the first partial refresh can safely merge.
        self.data = {}

    def _schedule(self, parking_id):
        values = self.schedules.get(parking_id, {})
        return {
            CONF_HIGH_INTERVAL: max(30, int(values.get(CONF_HIGH_INTERVAL, DEFAULT_HIGH_INTERVAL))),
            CONF_LOW_INTERVAL: max(60, int(values.get(CONF_LOW_INTERVAL, DEFAULT_LOW_INTERVAL))),
            CONF_DAY_START: _clock(values.get(CONF_DAY_START, DEFAULT_DAY_START), DEFAULT_DAY_START),
            CONF_NIGHT_START: _clock(values.get(CONF_NIGHT_START, DEFAULT_NIGHT_START), DEFAULT_NIGHT_START),
        }

    def _interval(self, parking_id, now):
        schedule = self._schedule(parking_id)
        current = now.timetz().replace(tzinfo=None)
        start, end = schedule[CONF_DAY_START], schedule[CONF_NIGHT_START]
        is_day = start <= current < end if start < end else (current >= start or current < end)
        return schedule[CONF_HIGH_INTERVAL] if is_day else schedule[CONF_LOW_INTERVAL]

    async def _async_update_data(self):
        """Update only parkings whose individual timer has expired."""
        now = dt_util.now()
        due = [pid for pid in self.selected if pid not in self._next_due or self._next_due[pid] <= now]
        if not due:
            return self.data

        self.last_attempt = now
        try:
            payload = await self.api.fetch()
            source = {str(item["id"]): item for item in payload["parking"] if "id" in item}
            missing = [pid for pid in due if pid not in source]
            if missing:
                _LOGGER.warning("VDL response did not include selected parking IDs: %s", missing)

            updated = dict(self.data)
            for parking_id in due:
                item = source.get(parking_id)
                if item is None:
                    continue
                total = int(item.get("total") or 0)
                available = int(item.get("actuel") or 0)
                occupied = max(total - available, 0)
                coords = item.get("coords") or {}
                updated[parking_id] = {
                    "id": parking_id,
                    "name": item.get("title", f"Parking {parking_id}"),
                    "open": bool(item.get("ouvert")),
                    "full": bool(item.get("complet")),
                    "out_of_service": bool(item.get("panne")),
                    "total_capacity": total,
                    "available_spaces": available,
                    "occupied_spaces": occupied,
                    "occupancy_rate": round(occupied / total * 100) if total else 0,
                    "latitude": coords.get("latitude"),
                    "longitude": coords.get("longitude"),
                    "last_updated": now,
                }
                self._next_due[parking_id] = now + timedelta(
                    seconds=self._interval(parking_id, now)
                )

            self.api_reachable = True
            self.last_success = now
            self.last_error = None
            self.consecutive_failures = 0
            return self.data
        except Exception as err:
            self.api_reachable = False
            self.last_error = str(err)[:250]
            self.consecutive_failures += 1
            _LOGGER.warning("VDL API update failed (%s consecutive failures): %s",
                            self.consecutive_failures, err)
            raise UpdateFailed(f"VDL API update failed: {err}") from err

    @property
    def health(self):
        """Return non-sensitive API health information."""
        return {
            "api_reachable": self.api_reachable,
            "last_attempt": self.last_attempt,
            "last_success": self.last_success,
            "last_error": self.last_error,
            "consecutive_failures": self.consecutive_failures,
        }
