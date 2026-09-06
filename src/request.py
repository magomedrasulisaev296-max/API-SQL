import requests

url = "https://hh.ru/?customDomain=1&overRideDomainAreaId=1"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print(f"Ошибка: {response.status_code}")
