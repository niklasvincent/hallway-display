import os
import pytz

from PIL import Image, ImageDraw, ImageFont


from sources.public_transport.client import PublicTransportClient
from config import BUS_STOPS


def main(sl_api_key):
    timezone = pytz.timezone("Europe/Stockholm")
    client = PublicTransportClient(api_key=sl_api_key, timezone=timezone)

    rows = []

    for bus_stop in BUS_STOPS:
        departures = client.get_bus_departures(bus_stop=bus_stop)
        for departure in departures:
            rows.append(
                (
                    bus_stop.abbreviated_name,
                    departure.line_number,
                    departure.destination,
                    departure.expected_formatted,
                )
            )
        rows.append(())
    
    print(rows)

    # rows = [
    #     ("E", "66", "Reimersholme", "11"),
    #     ("E", "2", "Norrtull", "21:49"),
    #     ("E", "2", "Norrtull", "22:04"),
    #     (),
    #     ("ES", "53", "Karolinska institutet", "7"),
    #     ("ES", "71", "Jarlaberg", "21:49"),
    #     ("ES", "53", "Karolinska institutet", "22:11"),
    #     (),
    #     ("Å", "3", "Karolinska institutet", "21:49"),
    #     ("Å", "76", "Ropsten", "21:52"),
    #     ("Å", "3", "Karolinska institutet", "22:04"),
    #     ("Å", "76", "Ropsten", "22:12"),
    # ]

    width = 800
    height = 600
    img = Image.new("RGB", (width, height), color="white")

    draw = ImageDraw.Draw(img)

    font_size = 40
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
