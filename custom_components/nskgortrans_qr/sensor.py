import re

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


MINUTES_INLINE_RE = re.compile(r"(\d+)\s*мин", re.IGNORECASE)
DIGITS_ONLY_RE = re.compile(r"^\d{1,3}$")
MAX_REASONABLE_MINUTES = 180


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


class NSKRouteSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, number, transport_type):
        super().__init__(coordinator)
        self.number = number
        self.transport_type = transport_type

        self._attr_name = f"Транспорт {number} {transport_type}"
        self._attr_unique_id = f"{number}_{transport_type}"
        self._attr_unit_of_measurement = "min"

    @property
    def state(self):
        if not self.coordinator.data:
            return "unknown"

        route_pattern = re.compile(rf"\b{re.escape(self.number)}\b", re.IGNORECASE)
        lines = [line.strip() for line in self.coordinator.data if line and line.strip()]

        for index, line in enumerate(lines):
            if not route_pattern.search(line):
                continue
            if self.transport_type.lower() not in line.lower():
                continue

            value = _extract_minutes_from_window(lines, index, self.number)
            if value is not None:
                return value

        for index, line in enumerate(lines):
            if not route_pattern.search(line):
                continue

            value = _extract_minutes_from_window(lines, index, self.number)
            if value is not None:
                return value

        return "unknown"


def _extract_minutes_from_window(lines, route_index, route_number):
    route_num_int = int(route_number) if route_number.isdigit() else None
    candidates = []

    # Inspect only lines after route row to avoid treating route number as ETA.
    window = lines[route_index + 1 : route_index + 9]

    for idx, line in enumerate(window):
        inline_match = MINUTES_INLINE_RE.search(line)
        if inline_match:
            minutes = int(inline_match.group(1))
            if 0 < minutes <= MAX_REASONABLE_MINUTES:
                candidates.append(minutes)
            continue

        if DIGITS_ONLY_RE.match(line):
            minutes = int(line)
            if route_num_int is not None and minutes == route_num_int:
                continue

            next_line = window[idx + 1] if idx + 1 < len(window) else ""
            if "мин" in next_line.lower() and 0 < minutes <= MAX_REASONABLE_MINUTES:
                candidates.append(minutes)

    if not candidates:
        return None

    return min(candidates)
