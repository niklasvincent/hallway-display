from datetime import datetime
from functools import wraps
from io import BytesIO

import pytz
from flask import Flask, jsonify, request, send_file
from flask_api import status
from PIL import Image, ImageDraw, ImageFont

from sources.openweather.client import OpenweatherClient
from sources.public_transport.client import PublicTransportClient
from config import BUS_STOPS
from utils.config import Config
from utils.logging import create_stdout_logger


def create_app():
    logger = create_stdout_logger(__name__)
    config = Config(logger)

    timezone = pytz.timezone("Europe/Stockholm")

    logger.info("Using timezone %s", timezone)

    logger.info("Creating client for SL traffic API")
    sl_client = PublicTransportClient(api_key=config.get("sl_api_key"))
    logger.info("Finished setting up client for SL traffic API")

    logger.info("Creating client for Openweather API")
    openweather_client = OpenweatherClient(
        logger=logger, api_key=config.get("openweather_api_key")
    )
    logger.info("Finished setting up client for Openweather API")

    server = Server(
        logger=logger,
        config=config,
        timezone=timezone,
        sl_client=sl_client,
        openweather_client=openweather_client,
    )

    app = Flask(__name__, instance_relative_config=True)

    def authorize(f):
        @wraps(f)
        def decorated_function(*args, **kws):
            data = request.headers.get("Authorization", "")

            if not data:
                data = request.args.get("auth_token", "")

            token = str.replace(str(data), "Bearer ", "")
            if not token == config.get("api_auth_token"):
                logger.error("Invalid auth token provided")
                return (
                    jsonify(status="Unauthorized"),
                    status.HTTP_401_UNAUTHORIZED,
                )

            return f(*args, **kws)

        return decorated_function

    def serve_pil_image(pil_img):
        img_io = BytesIO()
        pil_img.save(img_io, "PNG", dpi=(212, 212))
        img_io.seek(0)
        return send_file(img_io, mimetype="image/png")

    @app.route("/hallway-display.png", methods=["GET"])
    @authorize
    def render_next_frame():
        img = server.get_next_frame()
        return serve_pil_image(img)

    @app.route("/health-check", methods=["GET"])
    def health_check():
        return (
            jsonify(message="Success"),
            status.HTTP_200_OK,
        )

    @app.errorhandler(404)
    def endpoint_not_found(e):
        return jsonify(error=404, text=str(e)), status.HTTP_404_NOT_FOUND

    @app.errorhandler(500)
    def internal_server_error(e):
        return (
            jsonify(error=500, text="Something went wrong"),
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return app


class Server(object):
    def __init__(self, logger, config, timezone, sl_client, openweather_client):
        self.logger = logger
        self.config = config
        self.timezone = timezone
        self.sl_client = sl_client
        self.openweather_client = openweather_client

    def get_next_frame(self):
        current_time = datetime.now(self.timezone)
        departures_by_bus_stop = self._get_departures_by_bus_stop(
            current_time, BUS_STOPS
        )
        lat, lon = self.config.get("home_coordinates").split(",")
        weather_data = self.openweather_client.get_current_weather(lat=lat, lon=lon)
        return self._render_output_image(
            current_time=current_time,
            departures_by_bus_stop=departures_by_bus_stop,
            weather_data=weather_data,
        )

    def _get_departures_by_bus_stop(self, current_time, bus_stops):
        departures_by_bus_stop = []
        for bus_stop in bus_stops:
            self.logger.info(
                "Getting all departures from bus stop %s (%s)",
                bus_stop.name,
                bus_stop.site_id,
            )
            departures = self.sl_client.get_bus_departures(
                current_time=current_time, bus_stop=bus_stop
            )
            self.logger.info("Got %d departures", len(departures))
            for departure in departures:
                departures_by_bus_stop.append((bus_stop, departure))
        return departures_by_bus_stop

    def _render_output_image(self, current_time, departures_by_bus_stop, weather_data):
        self.logger.info("Construction rows of bus departures to render")
        rows = []

        current_bus_stop = departures_by_bus_stop[0][0]
        for bus_stop, departure in departures_by_bus_stop:
            if current_bus_stop != bus_stop:
                rows.append(("-"))
                current_bus_stop = bus_stop

            rows.append(
                (
                    bus_stop.abbreviated_name,
                    departure.line_number,
                    departure.destination,
                    departure.expected_formatted,
                )
            )

        rows.append("-")

        self.logger.info("Constructed %d rows of bus departures to render", len(rows))

        x_res = 1024
        y_res = 768
        self.logger.info("Starting rendering of output image (%d x %d)", x_res, y_res)

        img = Image.new("RGB", (x_res, y_res), color="white")

        draw = ImageDraw.Draw(img)

        font_size = 20 if len(rows) <= 13 else 15
        regular_font = ImageFont.truetype("fonts/FragmentMono-Regular.ttf", font_size)
        italic_font = ImageFont.truetype("fonts/FragmentMono-Italic.ttf", font_size)

        right_padding = 600
        spacing = 20
        x_offsets = [5, 80, 160]
        fonts = [regular_font, regular_font, regular_font, italic_font]
        x_offset = x_offsets[0]
        y_offset = 0

        for row in rows:
            for i, text in enumerate(row):
                font = fonts[i]
                if i == len(row) - 1:
                    x_offset = (
                        x_res
                        - draw.textlength(text, font=font)
                        - right_padding
                        - spacing / 2
                    )
                else:
                    x_offset = x_offsets[i]

                if text != "-":
                    draw.text(
                        xy=(x_offset, y_offset), text=text, fill=(0, 0, 0), font=font
                    )
                    x_offset += draw.textlength(text, font=font) + spacing

            if len(row) == 1 and row[0] == "-":
                y_offset_line = y_offset + font_size // 2.5
                draw.line(
                    (
                        0,
                        y_offset_line,
                        x_res - right_padding,
                        y_offset_line,
                    ),
                    fill=(125, 125, 125),
                    width=1,
                )
                y_offset += font_size / 2
            else:
                y_offset += font_size

            x_offset = 5

        draw.line(
            (
                x_res - right_padding,
                0,
                x_res - right_padding,
                y_offset,
            ),
            fill=(125, 125, 125),
            width=1,
        )

        # Current time and week
        week_number = "Week {}".format(current_time.isocalendar().week)
        current_time_formatted = current_time.strftime("%H:%M")
        draw.text(
            xy=(450, 0),
            text=current_time_formatted,
            fill=(0, 0, 0),
            font=font,
        )
        draw.text(
            xy=(450, font_size),
            text=week_number,
            fill=(0, 0, 0),
            font=font,
        )

        # Extract and display forecast data for the next 5 days
        # for entry in weather_data["list"]:
        #     timestamp = entry["dt"]
        #     date_time = datetime.fromtimestamp(timestamp)
        #     icon = Image.open(
        #         self.openweather_client.get_weather_icon(entry["weather"][0]["icon"])
        #     )

        #     # Calculate the x-coordinate based on the date
        #     x_coordinate = (date_time.day - datetime.now().day) * 120

        #     # Paste the icon on the image
        #     img.paste(icon, (x_coordinate, 400))

        #     # Draw temperature and date on the image
        #     draw.text(
        #         (x_coordinate, 430),
        #         f"{date_time.strftime('%H:%M')}",
        #         fill="black",
        #         font=font,
        #     )
        #     draw.text(
        #         (x_coordinate, 470),
        #         f"{entry['main']['temp']}°C",
        #         fill="black",
        #         font=font,
        #     )

        img = img.transpose(Image.ROTATE_90)

        return img
