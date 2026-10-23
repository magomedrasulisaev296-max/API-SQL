import requests


def get_country_coords(country_name):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"country": country_name, "format": "json", "limit": 1}
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 "
            "(magomedrasulisaev296@gmail.com)"
        )
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data:
            lat = data[0].get("lat")
            lon = data[0].get("lon")
            print(data)
            return {"lat": float(lat), "lon": float(lon)}
    return None
