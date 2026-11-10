
"""Per-parking polling coordinator and API health tracking."""

from datetime import datetime, time, timedelta
import logging

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.util import dt as dt_util

from .api import VdlParkingApi
from .const import (
    CONF_HIGH_INTERVAL,
    CONF_LOW_INTERVAL,
    CONF_DAY_START,
    CONF_NIGHT_START,
    DEFAULT_HIGH_INTERVAL,
    DEFAULT_LOW_INTERVAL,
    DEFAULT_DAY_START,
    DEFAULT_NIGHT_START,
    DOMAIN,
    SCHEDULER_TICK_SECONDS,
    get_parking_schedules,
    get_selected_parkings,
)

_LOGGER = logging.getLogger(__name__)


def _clock(value, fallback):
    """Parse a HH:MM value safely."""
    try:
        hour, minute = (int(part) for part in value.split(":"))

        if (
            len(value) != 5
            or value[2] != ":"
            or not 0 <= hour <= 23
            or not 0 <= minute <= 59
        ):
            raise ValueError

        return time(hour, minute)

    except (AttributeError, TypeError, ValueError):
        return time.fromisoformat(fallback)


class VdlParkingCoordinator(DataUpdateCoordinator):
    """Fetch the shared VDL feed when a selected parking is due."""

    def __init__(self, hass, entry):
        """Initialize the coordinator."""
        self.entry = entry
        self.api = VdlParkingApi(async_get_clientsession(hass))

        self.selected = set(get_selected_parkings(entry))
        self.schedules = get_parking_schedules(entry)

        self.last_success = None
        self.last_attempt = None
        self.last_error = None
        self.consecutive_failures = 0
        self.api_reachable = False

        self._next_due = {
            parking_id: datetime.min.replace(
                tzinfo=dt_util.DEFAULT_TIME_ZONE
            )
            for parking_id in self.selected
        }

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(
                seconds=SCHEDULER_TICK_SECONDS
            ),
        )

        # Keep previously fetched parking data between partial updates.
        self.data = {}

    def _schedule(self, parking_id):
        """Return a normalized schedule for one parking."""
        values = self.schedules.get(parking_id, {})

        try:
            high_interval = int(
                values.get(
                    CONF_HIGH_INTERVAL,
                    DEFAULT_HIGH_INTERVAL,
                )
            )
        except (TypeError, ValueError):
            high_interval = DEFAULT_HIGH_INTERVAL

        try:
            low_interval = int(
                values.get(
                    CONF_LOW_INTERVAL,
                    DEFAULT_LOW_INTERVAL,
                )
            )
        except (TypeError, ValueError):
            low_interval = DEFAULT_LOW_INTERVAL

        return {
            CONF_HIGH_INTERVAL: max(30, high_interval),
            CONF_LOW_INTERVAL: max(60, low_interval),
            CONF_DAY_START: _clock(
                values.get(CONF_DAY_START, DEFAULT_DAY_START),
                DEFAULT_DAY_START,
            ),
            CONF_NIGHT_START: _clock(
                values.get(CONF_NIGHT_START, DEFAULT_NIGHT_START),
                DEFAULT_NIGHT_START,
            ),
        }

    def _interval(self, parking_id, now):
        """Determine the current polling interval for one parking."""
        schedule = self._schedule(parking_id)

        current = now.timetz().replace(tzinfo=None)
        start = schedule[CONF_DAY_START]
        end = schedule[CONF_NIGHT_START]

        if start < end:
            is_day = start <= current < end
        else:
            # Also supports schedules spanning midnight.
            is_day = current >= start or current < end

        return (
            schedule[CONF_HIGH_INTERVAL]
            if is_day
            else schedule[CONF_LOW_INTERVAL]
        )

    async def _async_update_data(self):
        """Update parking records whose individual timers have expired."""
        now = dt_util.now()

        due = [
            parking_id
            for parking_id in self.selected
            if (
                parking_id not in self._next_due
                or self._next_due[parking_id] <= now
            )
        ]

        if not due:
            return self.data

        self.last_attempt = now

        try:
            # VDL returns all parking records in one response.
            # Individual schedules determine which records are updated.
            payload = await self.api.fetch()

            source = {
                str(item["id"]): item
                for item in payload["parking"]
                if "id" in item
            }

            missing = [
                parking_id
                for parking_id in due
                if parking_id not in source
            ]

            if missing:
                _LOGGER.warning(
                    "VDL response did not include selected parking IDs: %s",
                    missing,
                )

            updated = dict(self.data)

            for parking_id in due:
                item = source.get(parking_id)

                if item is None:
                    # Retry missing records at the next scheduler tick.
                    continue

                try:
                    total = int(item.get("total") or 0)
                    available = int(item.get("actuel") or 0)
                except (TypeError, ValueError) as err:
                    _LOGGER.warning(
                        "Invalid capacity data for parking %s: %s",
                        parking_id,
                        err,
                    )
                    continue

                occupied = max(total - available, 0)
                coords = item.get("coords") or {}

                updated[parking_id] = {
                    "id": parking_id,
                    "name": item.get(
                        "title",
                        f"Parking {parking_id}",
                    ),
                    "open": bool(item.get("ouvert")),
                    "full": bool(item.get("complet")),
                    "out_of_service": bool(item.get("panne")),
                    "total_capacity": total,
                    "available_spaces": available,
                    "occupied_spaces": occupied,
                    "occupancy_rate": (
                        round(occupied / total * 100)
                        if total
                        else 0
                    ),
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

            return updated

        except Exception as err:
            self.api_reachable = False
            self.last_error = str(err)[:250]
            self.consecutive_failures += 1

            _LOGGER.warning(
                "VDL API update failed (%s consecutive failures): %s",
                self.consecutive_failures,
                err,
            )

            raise UpdateFailed(
                f"VDL API update failed: {err}"
            ) from err

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

