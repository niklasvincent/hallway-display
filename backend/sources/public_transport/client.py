import json
from collections import defaultdict
from datetime import datetime
from math import floor
import requests

from requests_cache import CachedSession

from .model import BusStop, Departure


class PublicTransportClient(object):
    def __init__(self, api_key):
        self.api_key = api_key
        self.session = CachedSession(
            "sl_api_cache", ignored_parameters=["key"], expire_after=60
        )

    def _fetch_bus_departures(self, bus_stop, time_window=45):
        url = "https://api.sl.se/api2/realtimedeparturesV4.json?key={}&siteid={}&timewindow={}".format(
            self.api_key, bus_stop.site_id, time_window
        )
        response = self.session.get(url)

        if response.status_code == 200:
            data = response.json()
            return data.get("ResponseData", {}).get("Buses", [])
        else:
            self.logger.error("Got response code %s from SL API", response.status_code)
            raise Exception(
                "Could not fetch departures from SL for bus stop {}".format(
                    bus_stop.site_id
                )
            )

    def get_bus_departures(self, current_time, bus_stop, time_window=45):
        departures = self._fetch_bus_departures(
            bus_stop=bus_stop, time_window=time_window
        )

        buses_to_include = set(
            [
                (bus.line_number, bus.journey_direction)
                for bus in bus_stop.buses_to_include
            ]
        )

        all_departures = []

        for departure in departures:
            journey_direction = departure.get("JourneyDirection", None)
            line_number = departure.get("LineNumber", None)
            destination = departure.get("Destination", None)
            expected_date_time_raw = departure.get("ExpectedDateTime", None)

            if (
                journey_direction is None
                or line_number is None
                or destination is None
                or expected_date_time_raw is None
            ):
                continue

            if (str(line_number), int(journey_direction)) not in buses_to_include:
                continue

            if expected_date_time_raw is not None:
                expected_date_time = datetime.strptime(
                    expected_date_time_raw, "%Y-%m-%dT%H:%M:%S"
                )
                expected_time_delta = expected_date_time - current_time.replace(
                    tzinfo=None
                )
                # From <https://stackoverflow.com/a/796019>
                time_until_minutes = floor(expected_time_delta.seconds / 60)
                expected_formatted = ""
                if time_until_minutes >= 15:
                    expected_formatted = expected_date_time.strftime("%H:%M")
                else:
                    expected_formatted = str(time_until_minutes)
                if time_until_minutes < bus_stop.time_to_walk_minutes:
                    continue

                all_departures.append(
                    Departure(
                        line_number=line_number,
                        destination=destination,
                        expected=expected_date_time,
                        expected_formatted=expected_formatted,
                    )
                )

        filtered_departures = []
        occurences = defaultdict(int)

        all_departures.sort(key=lambda d: d.expected)
        for departure in all_departures:
            occurences[departure.line_number] += 1
            if occurences[departure.line_number] <= 2:
                filtered_departures.append(departure)

        return filtered_departures
