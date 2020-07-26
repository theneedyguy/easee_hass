""" easee services."""
import voluptuous as vol
import logging
from homeassistant.helpers import config_validation as cv
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

CHARGER_ID = "charger_id"
CIRCUIT_ID = "circuit_id"
ATTR_CHARGEPLAN_START_TIME = "chargeStartTime"
ATTR_CHARGEPLAN_STOP_TIME = "chargeStopTime"
ATTR_CHARGEPLAN_REPEAT = "repeat"
ATTR_SET_DYNAMIC_CURRENTP1 = "currentP1"
ATTR_SET_DYNAMIC_CURRENTP2 = "currentP2"
ATTR_SET_DYNAMIC_CURRENTP3 = "currentP3"

SERVICE_CHARGER_ACTION_COMMAND_SCHEMA = vol.Schema(
    {vol.Optional(CHARGER_ID): cv.string,}
)

SERVICE_CHARGER_SET_BASIC_CHARGEPLAN_SCHEMA = vol.Schema(
    {
        vol.Required(CHARGER_ID): cv.string,
        vol.Optional(ATTR_CHARGEPLAN_START_TIME): cv.time,
        vol.Optional(ATTR_CHARGEPLAN_STOP_TIME): cv.time,
        vol.Optional(ATTR_CHARGEPLAN_REPEAT): cv.boolean,
    }
)

SERVICE_CIRCUIT_SET_DYNAMIC_CURRENT_SCHEMA = vol.Schema(
    {
        vol.Required(CIRCUIT_ID): cv.positive_int,
        vol.Optional(ATTR_SET_DYNAMIC_CURRENTP1): cv.positive_int,
        vol.Optional(ATTR_SET_DYNAMIC_CURRENTP2): cv.positive_int,
        vol.Optional(ATTR_SET_DYNAMIC_CURRENTP3): cv.positive_int,
    }
)

SERVICE_MAP = {
    "start": {
        "handler": "charger_execute_service",
        "function_call": "start",
        "schema": SERVICE_CHARGER_ACTION_COMMAND_SCHEMA,
    },
    "stop": {
        "handler": "charger_execute_service",
        "function_call": "stop",
        "schema": SERVICE_CHARGER_ACTION_COMMAND_SCHEMA,
    },
    "pause": {
        "handler": "charger_execute_service",
        "function_call": "pause",
        "schema": SERVICE_CHARGER_ACTION_COMMAND_SCHEMA,
    },
    "resume": {
        "handler": "charger_execute_service",
        "function_call": "resume",
        "schema": SERVICE_CHARGER_ACTION_COMMAND_SCHEMA,
    },
    "toggle": {
        "handler": "charger_execute_service",
        "function_call": "toggle",
        "schema": SERVICE_CHARGER_ACTION_COMMAND_SCHEMA,
    },
    "override_schedule": {
        "handler": "charger_execute_service",
        "function_call": "override_schedule",
        "schema": SERVICE_CHARGER_ACTION_COMMAND_SCHEMA,
    },
    "smart_charging": {
        "handler": "charger_execute_service",
        "function_call": "smart_charging",
        "schema": SERVICE_CHARGER_ACTION_COMMAND_SCHEMA,
    },
    "reboot": {
        "handler": "charger_execute_service",
        "function_call": "reboot",
        "schema": SERVICE_CHARGER_ACTION_COMMAND_SCHEMA,
    },
    "update_firmware": {
        "handler": "charger_execute_service",
        "function_call": "update_firmware",
        "schema": SERVICE_CHARGER_ACTION_COMMAND_SCHEMA,
    },
    "get_basic_charge_plan": {
        "handler": "charger_execute_service",
        "function_call": "get_basic_charge_plan",
        "schema": SERVICE_CHARGER_ACTION_COMMAND_SCHEMA,
    },
    "set_basic_charge_plan": {
        "handler": "charger_execute_service",
        "function_call": "get_basic_charge_plan",
        "schema": SERVICE_CHARGER_SET_BASIC_CHARGEPLAN_SCHEMA,
    },
    "delete_basic_charge_plan": {
        "handler": "charger_execute_service",
        "function_call": "get_basic_charge_plan",
        "schema": SERVICE_CHARGER_ACTION_COMMAND_SCHEMA,
    },
    "set_dynamic_current": {
        "handler": "circuit_execute_set_dynamic_current",
        "function_call": "set_dynamic_current",
        "schema": SERVICE_CIRCUIT_SET_DYNAMIC_CURRENT_SCHEMA,
    },
}

async def async_setup_services(hass):
    """ Setup services for Easee """
    chargers = hass.data[DOMAIN]["chargers"]
    circuits = hass.data[DOMAIN]["circuits"]

    async def charger_execute_service(call):
        """Execute a service to Easee charging station. """
        charger_id = call.data.get(CHARGER_ID)

        _LOGGER.debug("execute_service:" + str(call.data))

        # Possibly move to use entity id later
        charger = next((c for c in chargers if c.id == charger_id), None)
        if charger:
            function_name = SERVICE_MAP[call.service]
            function_call = getattr(charger, function_name["function_call"])
            return await function_call()

        _LOGGER.error(
            "Could not find charger %s", charger_id,
        )
        raise HomeAssistantError("Could not find charger {}".format(charger_id))

    async def circuit_execute_set_dynamic_current(call):
        """Execute a service to Easee circuit. """
        circuit_id = call.data.get(CIRCUIT_ID)
        currentP1 = call.data.get(ATTR_SET_DYNAMIC_CURRENTP1)
        currentP2 = call.data.get(ATTR_SET_DYNAMIC_CURRENTP2)
        currentP3 = call.data.get(ATTR_SET_DYNAMIC_CURRENTP3)

        _LOGGER.debug("execute_service:" + str(call.data))

        circuit = next((c for c in circuits if c.id == circuit_id), None)
        if circuit:
            function_name = SERVICE_MAP[call.service]
            function_call = getattr(circuit, function_name["function_call"])
            return await function_call(currentP1, currentP2, currentP3)

        _LOGGER.error(
            "Could not find circuit %s", circuit_id,
        )
        raise HomeAssistantError("Could not find circuit {}".format(circuit_id))
   
    for service in SERVICE_MAP:
        data = SERVICE_MAP[service]
        handler = locals()[data["handler"]]
        hass.services.async_register(
            DOMAIN, service, handler, schema=data["schema"],
        )
