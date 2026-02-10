    @staticmethod
    def async_get_options_flow(config_entry):
        return NSKgortransQrOptionsFlow(config_entry)


class NSKgortransQrOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, entry):
        self.entry = entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            routes = self.entry.options.get("routes", [])
            routes.append(
                {
                    "number": user_input["number"],
                    "type": user_input["type"],
                }
            )

            return self.async_create_entry(
                title="",
                data={"routes": routes},
            )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required("number"): str,
                    vol.Required(
                        "type",
                        default="автобус",
                    ): vol.In(
                        [
                            "автобус",
                            "троллейбус",
                            "трамвай",
                            "маршрутное такси",
                        ]
                    ),
                }
            ),
        )
