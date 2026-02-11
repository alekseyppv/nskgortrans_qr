import re

from homeassistant.components.sensor import SensorEntity

from .const import DOMAIN


MINUTES_RE = re.compile(r"(\d+)\s*мин")


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    routes = entry.options.get("routes", entry.data.get("routes", []))

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
        if not self.coordinator.data:
            return "unknown"

        route_pattern = re.compile(rf"\b{re.escape(self.number)}\b")

        for line in self.coordinator.data:
            if not route_pattern.search(line):
                continue

            if self.transport_type in line:
                match = MINUTES_RE.search(line)
                if match:
                    return int(match.group(1))

        # fallback: if transport type text is absent on the page, use any matching route line
        for line in self.coordinator.data:
            if route_pattern.search(line):
                match = MINUTES_RE.search(line)
                if match:
                    return int(match.group(1))

        return "unknown"
