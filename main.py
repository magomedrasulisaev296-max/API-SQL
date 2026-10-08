import os

from dotenv import load_dotenv
from opensky_api import OpenSkyApi, TokenManager

from src.analyzer import Analyzer
from src.Classes import DBmanager
from src.openstreetmapapi import get_country_coords

load_dotenv()


def main():
    db = DBmanager()

    countries = ["Germany", "France", "Spain", "Italy"]

    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    if client_id and client_secret:
        tm = TokenManager(client_id=client_id, client_secret=client_secret)
        print("Authenticated with .env credentials.")
    else:
        tm = None
        print("No credentials found in .env, using anonymous access.")

    with OpenSkyApi(token_manager=tm) as api:
        for country in countries:
            coords = get_country_coords(country)
            if not coords:
                print(f"Не удалось получить координаты для {country}")
                continue

            lat = float(coords["lat"])
            lon = float(coords["lon"])

            print(f"\n--- Получаем данные для {country} (lat={lat}, lon={lon}) ---")

            bbox = (lat - 5, lat + 5, lon - 5, lon + 5)
            states = api.get_states(bbox=bbox)

            if states and states.states:
                analyzer = Analyzer(states.states)

                db.insert_countries_and_counts(analyzer.get_countries_and_aeroplanes_count())
                db.insert_all_aeroplanes(analyzer.get_all_aeroplanes())
                db.insert_avg_speed(analyzer.get_avg_speed())
                db.insert_high_speed_aircraft(analyzer.get_aeroplanes_with_higher_speed(threshold=200))

                print(f"Данные для {country} успешно сохранены в БД.")
            else:
                print(f"Нет данных для {country} (возможно, ограничение частоты запросов).")

    db.close()
    print("\nГотово! Все данные загружены.")


if __name__ == "__main__":
    main()
