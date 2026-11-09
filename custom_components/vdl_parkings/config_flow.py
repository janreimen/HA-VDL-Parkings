"""Config and options flows for VDL Parkings."""

import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import config_validation as cv

from .api import VdlParkingApi
from .const import (
    DOMAIN, CONF_PARKINGS, CONF_LANGUAGE, CONF_PARKING_SCHEDULES,
    CONF_HIGH_INTERVAL, CONF_LOW_INTERVAL, CONF_DAY_START, CONF_NIGHT_START,
    DEFAULT_HIGH_INTERVAL, DEFAULT_LOW_INTERVAL, DEFAULT_DAY_START,
    DEFAULT_NIGHT_START, LANGUAGES,
)

_LOGGER = logging.getLogger(__name__)


async def _get_parking_choices(hass):
    from homeassistant.helpers.aiohttp_client import async_get_clientsession
    payload = await VdlParkingApi(async_get_clientsession(hass)).fetch()
    items = payload["parking"]
    return {
        str(item["id"]): item.get("title", f"Parking {item['id']}")
        for item in sorted(items, key=lambda p: p.get("title", "").casefold())
    }


class VdlParkingConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Set up VDL Parkings."""

    VERSION = 2

    async def async_step_user(self, user_input=None):
        errors = {}
        try:
            choices = await _get_parking_choices(self.hass)
        except Exception:
            return self.async_abort(reason="cannot_connect")

        if user_input is not None:
            selected = user_input[CONF_PARKINGS]
            if not selected:
                errors["base"] = "select_at_least_one"
            else:
                schedules = {
                    parking_id: {
                        CONF_HIGH_INTERVAL: DEFAULT_HIGH_INTERVAL,
                        CONF_LOW_INTERVAL: DEFAULT_LOW_INTERVAL,
                        CONF_DAY_START: DEFAULT_DAY_START,
                        CONF_NIGHT_START: DEFAULT_NIGHT_START,
                    } for parking_id in selected
                }
                return self.async_create_entry(
                    title="VDL Parkings",
                    data={CONF_PARKINGS: selected, CONF_PARKING_SCHEDULES: schedules},
                    options={CONF_LANGUAGE: user_input[CONF_LANGUAGE]},
                )

        schema = vol.Schema({
            vol.Required(CONF_PARKINGS): cv.multi_select(choices),
            vol.Required(CONF_LANGUAGE, default="en"): vol.In(LANGUAGES),
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    def async_get_options_flow(config_entry):
        return VdlParkingOptionsFlow(config_entry)


class VdlParkingOptionsFlow(config_entries.OptionsFlow):
    """Allow changing selected parkings, language and per-parking polling."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        errors = {}
        try:
            choices = await _get_parking_choices(self.hass)
        except Exception:
            return self.async_abort(reason="cannot_connect")

        current = list(self.config_entry.data.get(CONF_PARKINGS, []))
        options = self.config_entry.options
        current_language = options.get(CONF_LANGUAGE, "en")
        if user_input is not None:
            selected = user_input[CONF_PARKINGS]
            if not selected:
                errors["base"] = "select_at_least_one"
            else:
                schedules = {}
                previous = options.get(CONF_PARKING_SCHEDULES,
                                       self.config_entry.data.get(CONF_PARKING_SCHEDULES, {}))
                for parking_id in selected:
                    old = previous.get(parking_id, {})
                    schedules[parking_id] = {
                        CONF_HIGH_INTERVAL: int(user_input.get(f"high_{parking_id}", old.get(CONF_HIGH_INTERVAL, DEFAULT_HIGH_INTERVAL))),
                        CONF_LOW_INTERVAL: int(user_input.get(f"low_{parking_id}", old.get(CONF_LOW_INTERVAL, DEFAULT_LOW_INTERVAL))),
                        CONF_DAY_START: user_input.get(f"day_{parking_id}", old.get(CONF_DAY_START, DEFAULT_DAY_START)),
                        CONF_NIGHT_START: user_input.get(f"night_{parking_id}", old.get(CONF_NIGHT_START, DEFAULT_NIGHT_START)),
                    }
                self.hass.config_entries.async_update_entry(
                    self.config_entry, data={**self.config_entry.data, CONF_PARKINGS: selected}
                )
                return self.async_create_entry(title="", data={
                    CONF_LANGUAGE: user_input[CONF_LANGUAGE],
                    CONF_PARKING_SCHEDULES: schedules,
                })

        schema_fields = {
            vol.Required(CONF_PARKINGS, default=current): cv.multi_select(choices),
            vol.Required(CONF_LANGUAGE, default=current_language): vol.In(LANGUAGES),
        }
        previous = options.get(CONF_PARKING_SCHEDULES,
                               self.config_entry.data.get(CONF_PARKING_SCHEDULES, {}))
        for parking_id in current:
            title = choices.get(parking_id, f"Parking {parking_id}")
            values = previous.get(parking_id, {})
            schema_fields[vol.Optional(f"high_{parking_id}", description={"suggested_value": values.get(CONF_HIGH_INTERVAL, DEFAULT_HIGH_INTERVAL)})] = vol.All(vol.Coerce(int), vol.Range(min=30, max=86400))
            schema_fields[vol.Optional(f"low_{parking_id}", description={"suggested_value": values.get(CONF_LOW_INTERVAL, DEFAULT_LOW_INTERVAL)})] = vol.All(vol.Coerce(int), vol.Range(min=60, max=86400))
            schema_fields[vol.Optional(f"day_{parking_id}", description={"suggested_value": values.get(CONF_DAY_START, DEFAULT_DAY_START)})] = str
            schema_fields[vol.Optional(f"night_{parking_id}", description={"suggested_value": values.get(CONF_NIGHT_START, DEFAULT_NIGHT_START)})] = str

        return self.async_show_form(step_id="init", data_schema=vol.Schema(schema_fields), errors=errors)
