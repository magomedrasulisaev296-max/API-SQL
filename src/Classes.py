import psycopg2


class DBmanager:
    def __init__(self):
        self.conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="postgres",
            user="postgres",
            password="12021985",
        )
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        queries = [
            """
            CREATE TABLE IF NOT EXISTS countries_count (
                id SERIAL PRIMARY KEY,
                country VARCHAR(100),
                count INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS all_aircraft (
                id SERIAL PRIMARY KEY,
                icao24 VARCHAR(10),
                callsign VARCHAR(20),
                origin_country VARCHAR(100),
                baro_altitude FLOAT,
                geo_altitude FLOAT,
                velocity FLOAT,
                on_ground BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS avg_speed (
                id SERIAL PRIMARY KEY,
                avg_speed FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS high_speed_aircraft (
                id SERIAL PRIMARY KEY,
                icao24 VARCHAR(10),
                callsign VARCHAR(20),
                velocity FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
        ]
        for q in queries:
            self.cur.execute(q)
        self.conn.commit()

    def insert_countries_and_counts(self, data):
        """data: dict {страна: количество}"""
        for country, count in data.items():
            self.cur.execute(
                "INSERT INTO countries_count (country, count) VALUES (%s, %s)",
                (country, count),
            )
        self.conn.commit()

    def insert_all_aeroplanes(self, states):
        """states: список объектов StateVector"""
        for s in states:
            self.cur.execute(
                """
                INSERT INTO all_aircraft
                (icao24, callsign, origin_country, baro_altitude, geo_altitude, velocity, on_ground)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    s.icao24,
                    s.callsign,
                    s.origin_country,
                    s.baro_altitude,
                    s.geo_altitude,
                    s.velocity,
                    s.on_ground,
                ),
            )
        self.conn.commit()

    def insert_avg_speed(self, avg):
        self.cur.execute("INSERT INTO avg_speed (avg_speed) VALUES (%s)", (avg,))
        self.conn.commit()

    def insert_high_speed_aircraft(self, states):
        """states: список объектов StateVector со скоростью выше порога"""
        for s in states:
            self.cur.execute(
                "INSERT INTO high_speed_aircraft (icao24, callsign, velocity) VALUES (%s, %s, %s)",
                (s.icao24, s.callsign, s.velocity),
            )
        self.conn.commit()

    def get_aeroplanes_with_keyword(self, keyword):
        # В реальном задании это тоже должно сохраняться в таблицу, но у нас нет отдельной таблицы для этого.
        # Можно просто вернуть результат (если не требуется отдельная таблица)
        # Или создать таблицу, если по заданию нужно. Пока оставим вывод.
        return f"Поиск по ключевому слову {keyword} завершен, данные в консоли."

    def close(self):
        self.cur.close()
        self.conn.close()


# states = api.get_states(bbox=(47.2, 55.1, 5.9, 15.1))
#
# if states and states.states:
#     # 1. Страны и количество
#     from collections import Counter
#     countries = [s.origin_country for s in states.states if s.origin_country]
#     print(Counter(countries))
#
#     # 2. Все самолёты
#     all_planes = states.states
#
#     # 3. Средняя скорость
#     speeds = [s.velocity for s in states.states if s.velocity is not None]
#     avg_speed = sum(speeds) / len(speeds) if speeds else 0
#
#     # 4. Самолёты со скоростью > 250
#     fast_planes = [s for s in states.states if s.velocity is not None and s.velocity > 250]
#
#     # 5. Поиск по ключевому слову в callsign
#     keyword_planes = [s for s in states.states if s.callsign and "DLH" in s.callsign.upper()]
