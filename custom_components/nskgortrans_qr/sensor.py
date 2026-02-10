from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    routes = entry.data["routes"]

    sensors = []
    for route in routes:
        sensors.append(
            NSKRouteSensor(
                coordinator,
                route["number"],
                route["type"],
            )
        )

    async_add_entities(sensors)


class NSKRouteSensor(SensorEntity):
    def __init__(self, coordinator, number, transport_type):
        self.coordinator = coordinator
        self.number = number
        self.transport_type = transport_type

        self._attr_name = f"Транспорт {number} {transport_type}"
        self._attr_unique_id = f"{number}_{transport_type}"
        self._attr_unit_of_measurement = "min"

    @property
    def available(self):
        return self.coordinator.last_update_success

    @property
    def state(self):
        for line in self.coordinator.data:
            if self.number in line and self.transport_type in line:
                for token in line.split():
                    if token.isdigit():
                        return int(token)
        return "unknown"
