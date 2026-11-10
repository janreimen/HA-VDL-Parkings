
"""Config and options flows for VDL Parkings."""

import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import config_validation as cv

from .api import VdlParkingApi
from .const import (
    DOMAIN,
    CONF_PARKINGS,
    CONF_LANGUAGE,
    CONF_PARKING_SCHEDULES,
    CONF_HIGH_INTERVAL,
    CONF_LOW_INTERVAL,
    CONF_DAY_START,
    CONF_NIGHT_START,
    DEFAULT_HIGH_INTERVAL,
    DEFAULT_LOW_INTERVAL,
    DEFAULT_DAY_START,
    DEFAULT_NIGHT_START,
    LANGUAGES,
)

_LOGGER = logging.getLogger(__name__)


async def _get_parking_choices(hass):
    """Retrieve available parking facilities from the VDL API."""
    from homeassistant.helpers.aiohttp_client import async_get_clientsession

    payload = await VdlParkingApi(
        async_get_clientsession(hass)
    ).fetch()

    items = payload["parking"]

    return {
        str(item["id"]): item.get("title", f"Parking {item['id']}")
        for item in sorted(
            items,
            key=lambda parking: parking.get("title", "").casefold(),
        )
        if "id" in item
    }


def _valid_clock(value):
    """Validate a 24-hour HH:MM value."""
    if not isinstance(value, str):
        raise vol.Invalid("Time must use HH:MM format")

    try:
        hour, minute = (int(part) for part in value.split(":"))
    except (TypeError, ValueError):
        raise vol.Invalid("Time must use HH:MM format") from None

    if (
        len(value) != 5
        or value[2] != ":"
        or not 0 <= hour <= 23
        or not 0 <= minute <= 59
    ):
        raise vol.Invalid("Time must use HH:MM format")

    return value


def _default_schedule():
    """Return a fresh default polling schedule."""
    return {
        CONF_HIGH_INTERVAL: DEFAULT_HIGH_INTERVAL,
        CONF_LOW_INTERVAL: DEFAULT_LOW_INTERVAL,
        CONF_DAY_START: DEFAULT_DAY_START,
        CONF_NIGHT_START: DEFAULT_NIGHT_START,
    }


class VdlParkingConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Set up VDL Parkings."""

    VERSION = 3

    async def async_step_user(self, user_input=None):
        """Handle the initial setup."""
        errors = {}

        try:
            choices = await _get_parking_choices(self.hass)
        except Exception:
            _LOGGER.exception("Unable to retrieve VDL parking facilities")
            return self.async_abort(reason="cannot_connect")

        if user_input is not None:
            selected = user_input[CONF_PARKINGS]

            if not selected:
                errors["base"] = "select_at_least_one"
            else:
                schedules = {
                    parking_id: _default_schedule()
                    for parking_id in selected
                }

                return self.async_create_entry(
                    title="VDL Parkings",
                    data={
                        CONF_PARKINGS: selected,
                        CONF_PARKING_SCHEDULES: schedules,
                    },
                    options={
                        CONF_LANGUAGE: user_input[CONF_LANGUAGE],
                        CONF_PARKING_SCHEDULES: schedules,
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_PARKINGS): cv.multi_select(choices),
                vol.Required(
                    CONF_LANGUAGE,
                    default="en",
                ): vol.In(LANGUAGES),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        """Return the options flow."""
        return VdlParkingOptionsFlow()


class VdlParkingOptionsFlow(config_entries.OptionsFlowWithReload):
    """Configure selected parkings and individual polling schedules."""

    async def async_step_init(self, user_input=None):
        """Manage integration options."""
        entry = self.config_entry
        errors = {}

        try:
            choices = await _get_parking_choices(self.hass)
        except Exception:
            _LOGGER.exception("Unable to retrieve VDL parking facilities")
            return self.async_abort(reason="cannot_connect")

        previous_schedules = entry.options.get(
            CONF_PARKING_SCHEDULES,
            entry.data.get(CONF_PARKING_SCHEDULES, {}),
        )

        current_parkings = entry.options.get(
            CONF_PARKINGS,
            entry.data.get(CONF_PARKINGS, []),
        )

        current_language = entry.options.get(
            CONF_LANGUAGE,
            "en",
        )

        if user_input is not None:
            selected = user_input[CONF_PARKINGS]

            if not selected:
                errors["base"] = "select_at_least_one"
            else:
                schedules = {}

                for parking_id in selected:
                    old_schedule = previous_schedules.get(
                        parking_id,
                        _default_schedule(),
                    )

                    schedules[parking_id] = {
                        CONF_HIGH_INTERVAL: int(
                            user_input.get(
                                f"high_{parking_id}",
                                old_schedule.get(
                                    CONF_HIGH_INTERVAL,
                                    DEFAULT_HIGH_INTERVAL,
                                ),
                            )
                        ),
                        CONF_LOW_INTERVAL: int(
                            user_input.get(
                                f"low_{parking_id}",
                                old_schedule.get(
                                    CONF_LOW_INTERVAL,
                                    DEFAULT_LOW_INTERVAL,
                                ),
                            )
                        ),
                        CONF_DAY_START: user_input.get(
                            f"day_{parking_id}",
                            old_schedule.get(
                                CONF_DAY_START,
                                DEFAULT_DAY_START,
                            ),
                        ),
                        CONF_NIGHT_START: user_input.get(
                            f"night_{parking_id}",
                            old_schedule.get(
                                CONF_NIGHT_START,
                                DEFAULT_NIGHT_START,
                            ),
                        ),
                    }

                return self.async_create_entry(
                    title="",
                    data={
                        CONF_PARKINGS: selected,
                        CONF_LANGUAGE: user_input[CONF_LANGUAGE],
                        CONF_PARKING_SCHEDULES: schedules,
                    },
                )

        schema_fields = {
            vol.Required(
                CONF_PARKINGS,
                default=current_parkings,
            ): cv.multi_select(choices),
            vol.Required(
                CONF_LANGUAGE,
                default=current_language,
            ): vol.In(LANGUAGES),
        }

        for parking_id in current_parkings:
            values = previous_schedules.get(
                parking_id,
                _default_schedule(),
            )

            schema_fields[
                vol.Optional(
                    f"high_{parking_id}",
                    description={
                        "suggested_value": values.get(
                            CONF_HIGH_INTERVAL,
                            DEFAULT_HIGH_INTERVAL,
                        )
                    },
                )
            ] = vol.All(
                vol.Coerce(int),
                vol.Range(min=30, max=86400),
            )

            schema_fields[
                vol.Optional(
                    f"low_{parking_id}",
                    description={
                        "suggested_value": values.get(
                            CONF_LOW_INTERVAL,
                            DEFAULT_LOW_INTERVAL,
                        )
                    },
                )
            ] = vol.All(
                vol.Coerce(int),
                vol.Range(min=60, max=86400),
            )

            schema_fields[
                vol.Optional(
                    f"day_{parking_id}",
                    description={
                        "suggested_value": values.get(
                            CONF_DAY_START,
                            DEFAULT_DAY_START,
                        )
                    },
                )
            ] = _valid_clock

            schema_fields[
                vol.Optional(
                    f"night_{parking_id}",
                    description={
                        "suggested_value": values.get(
                            CONF_NIGHT_START,
                            DEFAULT_NIGHT_START,
                        )
                    },
                )
            ] = _valid_clock

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(schema_fields),
            errors=errors,
        )

