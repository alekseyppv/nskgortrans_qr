import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, TRANSPORT_TYPES

class NSKgortransQrConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title="NSKGorTrans QR",
                data=user_input,
            )

        schema = vol.Schema({
            vol.Required("url"): str,
            vol.Required("scan_interval", default=60): vol.All(
                vol.Coerce(int), vol.Range(min=30, max=600)
            ),
            vol.Required("routes"): [
                {
                    vol.Required("number"): str,
                    vol.Required("type"): vol.In(TRANSPORT_TYPES),
                }
            ],
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
        )
