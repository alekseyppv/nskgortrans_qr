import logging
from datetime import timedelta

import aiohttp
from bs4 import BeautifulSoup
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)


class NSKCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, url, scan_interval):
        super().__init__(
            hass,
            logger=_LOGGER,
            name="nskgortrans_qr",
            update_interval=timedelta(seconds=scan_interval),
        )
        self.url = url

    async def _async_update_data(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url, timeout=10) as resp:
                    text = await resp.text()
        except Exception as err:
            raise UpdateFailed(err) from err

        soup = BeautifulSoup(text, "html.parser")

        # Keep all non-empty visible lines; some pages split route/type/minutes
        # across neighboring rows, so filtering only lines with "мин." loses data.
        lines = [line.strip() for line in soup.get_text("\n").splitlines() if line.strip()]

        return lines
