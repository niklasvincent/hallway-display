from io import BytesIO
from collections import defaultdict
from datetime import timedelta, datetime
from math import floor
import requests

from requests_cache import CachedSession


class OpenweatherClient(object):
    def __init__(self, logger, api_key):
        self.logger = logger
        self.api_key = api_key
        self.session = CachedSession(
            "openweather_api_cache", ignored_parameters=["appid"], expire_after=900
        )
        self.icon_session = CachedSession(
            "openweather_icon_cache", expire_after=timedelta(days=30)
        )

    def _fetch_current_weather(self, lat, lon):
        base_url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {"lat": lat, "lon": lon, "units": "metric", "appid": self.api_key}

        response = self.session.get(base_url, params=params)

        if response.status_code == 200:
            weather_data = response.json()
            return weather_data
        else:
            self.logger.error(
                "Got response code %s from Openweather API", response.status_code
            )

        return None

    def get_weather_icon(self, icon_code):
        icon_url = f"http://openweathermap.org/img/w/{icon_code}.png"
        icon_response = self.icon_session.get(icon_url)
        return BytesIO(icon_response.content)

    def get_current_weather(self, lat, lon):
        return self._fetch_current_weather(lat, lon)
