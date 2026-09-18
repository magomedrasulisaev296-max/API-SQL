import os
from dotenv import load_dotenv
from opensky_api import OpenSkyApi, TokenManager
from src.openstreetmapapi import get_country_coords

load_dotenv()


def fmt_alt(value):
    return f"{value}m" if value is not None else "None"


def main():
    country = "Germany"
    coords = get_country_coords(country)

    if not coords:
        print(f"Не удалось получить координаты для {country}")
        return

    lat = float(coords["lat"])
    lon = float(coords["lon"])
    print(f"Координаты {country}: lat={lat}, lon={lon}")

    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    if client_id and client_secret:
        tm = TokenManager(client_id=client_id, client_secret=client_secret)
        print("Authenticated with .env credentials.")
    else:
        tm = None
        print("No credentials found in .env, using anonymous access.")

    with OpenSkyApi(token_manager=tm) as api:
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