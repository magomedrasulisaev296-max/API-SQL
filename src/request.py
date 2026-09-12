import os

from opensky_api import OpenSkyApi, TokenManager

from src.openstreetmapapi import get_country_coords  # твой модуль

_CREDENTIALS_PATH = "credentials.json"


def fmt_alt(value):
    return f"{value}m" if value is not None else "None"


def main():
    country = "Germany"  # или любая другая страна
    coords = get_country_coords(country)

    if not coords:
        print(f"Не удалось получить координаты для {country}")
        return

    # Берём lat и lon из первого результата
    lat = float(coords["lat"])
    lon = float(coords["lon"])

    print(f"Координаты {country}: lat={lat}, lon={lon}") # from openstreetmapapi

    if os.path.exists(_CREDENTIALS_PATH):
        tm = TokenManager.from_json_file(_CREDENTIALS_PATH)
        print("Authenticated with credentials file.")
    else:
        tm = None
        print(
            "No credentials file found, using anonymous access (reduced rate limits)."
        )

    with OpenSkyApi(token_manager=tm) as api:
        # Используем bbox вокруг координат (примерно 2 градуса в каждую сторону)
        bbox = (lat - 2, lat + 2, lon - 2, lon + 2)
        print(f"\n--- Aircraft near {country} (bbox={bbox}) ---")

        states = api.get_states(bbox=bbox)

        if states and states.states:
            for s in states.states:
                print(
                    f"{s.icao24:8s}  {s.callsign or '?':10s}  {s.origin_country:20s}  "
                    f"baro={fmt_alt(s.baro_altitude)}  "
                    f"geo={fmt_alt(s.geo_altitude)}  "
                    f"{'on ground' if s.on_ground else 'airborne'}"
                )
        else:
            print("No states received.")


if __name__ == "__main__":
    main()
