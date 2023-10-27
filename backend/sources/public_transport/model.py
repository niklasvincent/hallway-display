from collections import namedtuple

TOWARDS_CENTRE = 2
AWAY_FROM_CENTRE = 1


Departure = namedtuple(
    "Departure", ["line_number", "destination", "expected", "expected_formatted"]
)


BusStop = namedtuple(
    "BusStop",
    [
        "name",
        "abbreviated_name",
        "site_id",
        "direction_of_interest",
        "buses_to_include",
        "time_to_walk_minutes",
    ],
)

Bus = namedtuple("Bus", ["line_number", "journey_direction"])
