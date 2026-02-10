import aiohttp
from bs4 import BeautifulSoup
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

class NSKCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, url, scan_interval):
        super().__init__(
            hass,
            logger=None,
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
            raise UpdateFailed(err)

        soup = BeautifulSoup(text, "html.parser")
        lines = soup.get_text("\n").splitlines()

        result = []
        for line in lines:
            if "мин." in line:
                result.append(line.strip())

        return result
