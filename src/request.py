import time

import requests

from src.Classes import DBManager
from src.openstreetmapapi import get_country_coords


def get_states(bbox):
    """Получение состояний самолётов из OpenSky без токена."""
    url = "https://opensky-network.org/api/states/all"
    params = {
        "lamin": bbox[0],
        "lamax": bbox[1],
        "lomin": bbox[2],
        "lomax": bbox[3],
    }
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        return response.json().get("states") or []
    print(f"OpenSky error: {response.status_code}")
    return []


def main():
    db = DBManager()

    countries = ["Germany", "France", "Spain", "Italy"]

    for country in countries:
        coords = get_country_coords(country)
        if not coords:
            print(f"Не удалось получить координаты для {country}")
            continue

        lat = coords["lat"]
        lon = coords["lon"]
        print(f"\n--- {country} (lat={lat}, lon={lon}) ---")

        bbox = (lat - 5, lat + 5, lon - 5, lon + 5)
        states = get_states(bbox)

        if states:
            # Преобразуем сырые списки в объекты, которые ждёт DBManager
            class State:
                def __init__(self, row):
                    self.icao24 = row[0]
                    self.callsign = row[1]
                    self.origin_country = row[2]
                    self.baro_altitude = row[13]
                    self.geo_altitude = row[13]
                    self.velocity = row[9]
                    self.on_ground = row[8]

            state_objects = [State(row) for row in states]

            db.insert_all_aeroplanes(state_objects)
            print(f"Сохранено {len(state_objects)} самолётов для {country}")

        time.sleep(2)  # не спамим API

    # Считаем количество по странам из уже собранных данных
    from collections import Counter
    all_data = db.get_all_aeroplanes()
    counts = Counter(row[3] for row in all_data if row[3])
    db.insert_countries_and_counts(dict(counts))

    print("\n--- Итог ---")
    print("Страны:", db.get_countries_and_aeroplanes_count())
    print("Средняя скорость:", db.get_avg_speed())
    print("Быстрые:", db.get_aeroplanes_with_higher_speed()[:3])
    print("ACA:", db.get_aeroplanes_with_keyword("ACA"))

    db.close()


if __name__ == "__main__":
    main()
