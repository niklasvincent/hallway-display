import os
import pytz
from collections import defaultdict

from PIL import Image, ImageDraw, ImageFont


from sources.public_transport.client import PublicTransportClient
from config import BUS_STOPS
from utils.logging import create_stdout_logger


def main(sl_api_key, timezone=pytz.timezone("Europe/Stockholm")):
    logger = create_stdout_logger("server")

    logger.info("Using timezone %s", timezone)

    logger.info("Creating client for SL traffic API")
    client = PublicTransportClient(api_key=sl_api_key, timezone=timezone)
    logger.info("Finished setting up client for SL traffic API")

    departures_by_bus_stop = get_departures_by_bus_stop(logger, client, BUS_STOPS)

    render_output_image(logger, departures_by_bus_stop=departures_by_bus_stop)


def get_departures_by_bus_stop(logger, client, bus_stops):
    departures_by_bus_stop = []
    for bus_stop in BUS_STOPS:
        logger.info(
            "Getting all departures from bus stop %s (%s)",
            bus_stop.name,
            bus_stop.site_id,
        )
        departures = client.get_bus_departures(bus_stop=bus_stop)
        logger.info("Got %d departures", len(departures))
        for departure in departures:
            departures_by_bus_stop.append((bus_stop, departure))
    return departures_by_bus_stop


def render_output_image(logger, departures_by_bus_stop):
    logger.info("Construction rows of bus departures to render")
    rows = []

    current_bus_stop = departures_by_bus_stop[0][0]
    for bus_stop, departure in departures_by_bus_stop:
        if current_bus_stop != bus_stop:
            rows.append(())
            current_bus_stop = bus_stop

        rows.append(
            (
                bus_stop.abbreviated_name,
                departure.line_number,
                departure.destination,
                departure.expected_formatted,
            )
        )

    print(rows)

    width = 800
    height = 600
    logger.info("Starting rendering of output image (%d x %d)", width, height)

    img = Image.new("RGB", (width, height), color="white")

    draw = ImageDraw.Draw(img)

    font_size = 30
    regular_font = ImageFont.truetype("fonts/CamingoCode-Regular.ttf", font_size)
    bold_font = ImageFont.truetype("fonts/CamingoCode-Bold.ttf", font_size)
    italic_font = ImageFont.truetype("fonts/CamingoCode-Italic.ttf", font_size)

    left_padding = 20
    spacing = 20
    x_offsets = [5, 80, 160]
    fonts = [regular_font, bold_font, regular_font, italic_font]
    x_offset = x_offsets[0]
    y_offset = 5

    for row in rows:
        for i, text in enumerate(row):
            font = fonts[i]
            if i == len(row) - 1:
                x_offset = width - draw.textlength(text, font=font) - left_padding
            else:
                x_offset = x_offsets[i]

            draw.text(xy=(x_offset, y_offset), text=text, fill=(0, 0, 0), font=font)
            x_offset += draw.textlength(text, font=font) + spacing

        if len(row) == 0:
            y_offset += font_size / 2
        else:
            y_offset += font_size

        x_offset = 5

    img.save("result.png")


if __name__ == "__main__":
    main(sl_api_key=os.environ.get("SL_API_KEY"))
