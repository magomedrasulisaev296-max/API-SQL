from collections import Counter


class Analyzer:
    def __init__(self, states):
        self.states = states  # список объектов StateVector

    def get_countries_and_aeroplanes_count(self):
        """Возвращает словарь {страна: количество самолетов}."""
        countries = [s.origin_country for s in self.states if s.origin_country]
        return dict(Counter(countries))

    def get_all_aeroplanes(self):
        """Возвращает список всех самолетов (объектов StateVector)."""
        return self.states

    def get_avg_speed(self):
        """Возвращает среднюю скорость всех самолетов."""
        speeds = [s.velocity for s in self.states if s.velocity is not None]
        return sum(speeds) / len(speeds) if speeds else 0.0

    def get_aeroplanes_with_higher_speed(self, threshold=200):
        """Возвращает список самолетов со скоростью выше заданного порога."""
        return [
            s for s in self.states if s.velocity is not None and s.velocity > threshold
        ]

    def get_aeroplanes_with_keyword(self, keyword):
        """Возвращает список самолетов, в позывном которых есть ключевое слово."""
        keyword = keyword.upper()
        return [s for s in self.states if s.callsign and keyword in s.callsign.upper()]
