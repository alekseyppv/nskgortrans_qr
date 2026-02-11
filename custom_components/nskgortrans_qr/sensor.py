import re

from homeassistant.components.sensor import SensorEntity

from .const import DOMAIN


MINUTES_RE = re.compile(r"(\d+)\s*мин", re.IGNORECASE)


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

        route_pattern = re.compile(rf"\b{re.escape(self.number)}\b", re.IGNORECASE)
        lines = [line for line in self.coordinator.data if line]

        # 1) Best case: route, type and minutes are all in one line.
        for line in lines:
            if not route_pattern.search(line):
                continue

            if self.transport_type.lower() in line.lower():
                match = MINUTES_RE.search(line)
                if match:
                    return int(match.group(1))

        # 2) Common QR layout: route in one row, minutes in the next row.
        for index, line in enumerate(lines):
            if not route_pattern.search(line):
                continue

            nearby = " ".join(lines[index : index + 4])
            match = MINUTES_RE.search(nearby)
            if match:
                return int(match.group(1))

        # 3) Fallback: ignore transport type and return first route match with minutes.
        for line in lines:
            if route_pattern.search(line):
                match = MINUTES_RE.search(line)
                if match:
                    return int(match.group(1))

        return "unknown"
