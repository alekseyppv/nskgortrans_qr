import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector
from .const import DOMAIN, TRANSPORT_TYPES


class NSKgortransQrConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self._config_data = {}
        self._routes = []

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            self._config_data = {
                "url": user_input["url"],
                "scan_interval": user_input["scan_interval"],
            }
            self._routes = []
            return await self.async_step_routes()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("url"): str,
                    vol.Required("scan_interval", default=60): vol.All(
                        vol.Coerce(int), vol.Range(min=30, max=600)
                    ),
                }
            ),
        )

    async def async_step_routes(self, user_input=None):
        errors = {}

        if user_input is not None:
            route_number = user_input["number"].strip()
            route_type = user_input["type"]

            if not route_number:
                errors["number"] = "invalid_route"
            else:
                self._routes.append(
                    {
                        "number": route_number,
                        "type": route_type,
                    }
                )

                if not user_input["add_another"]:
                    data = {**self._config_data, "routes": self._routes}
                    return self.async_create_entry(
                        title="NSKGorTrans QR",
                        data=data,
                    )

        return self.async_show_form(
            step_id="routes",
            data_schema=vol.Schema(
                {
                    vol.Required("number"): str,
                    vol.Required("type", default=TRANSPORT_TYPES[0]): selector.SelectSelector(
                        selector.SelectSelectorConfig(options=TRANSPORT_TYPES)
                    ),
                    vol.Required("add_another", default=False): bool,
                }
            ),
            description_placeholders={
                "routes_count": str(len(self._routes)),
            },
            errors=errors,
        )
