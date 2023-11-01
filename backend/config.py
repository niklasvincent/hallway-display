from collections import namedtuple
from sources.public_transport.model import (
    Bus,
    BusStop,
    TOWARDS_CENTRE,
    AWAY_FROM_CENTRE,
)


BUS_STOPS = [
    BusStop(
        name="Erstagatan",
        abbreviated_name="E",
        site_id=1304,
        direction_of_interest=2,
        buses_to_include=[
            Bus(line_number="2", journey_direction=TOWARDS_CENTRE),
            Bus(line_number="66", journey_direction=TOWARDS_CENTRE),
        ],
        time_to_walk_minutes=0,
    ),
    BusStop(
        name="Ersta sjukhus",
        abbreviated_name="ES",
        site_id=1305,
        direction_of_interest=2,
        buses_to_include=[
            Bus(line_number="53", journey_direction=TOWARDS_CENTRE),
            Bus(line_number="71", journey_direction=AWAY_FROM_CENTRE),

        ],
        time_to_walk_minutes=4,
    ),
    BusStop(
        name="Åsögatan",
        abbreviated_name="Å",
        site_id=1308,
        direction_of_interest=2,
        buses_to_include=[
            Bus(line_number="3", journey_direction=TOWARDS_CENTRE),
            Bus(line_number="76", journey_direction=TOWARDS_CENTRE),
        ],
        time_to_walk_minutes=10,
    ),
]
