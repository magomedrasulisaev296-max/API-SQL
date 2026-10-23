import psycopg2


class DBManager:
    def __init__(self, host="localhost", port="5432", database="postgres",
                 user="postgres", password="12021985"):
        self.conn = psycopg2.connect(
            host=host, port=port, database=database,
            user=user, password=password
        )
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        queries = [
            """
            CREATE TABLE IF NOT EXISTS countries (
                id SERIAL PRIMARY KEY,
                country VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS aircrafts (
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
        ]
        for q in queries:
            self.cur.execute(q)
        self.conn.commit()

    # ---------- INSERT ----------

    def insert_country(self, country):
        """Добавляет страну в таблицу countries."""
        self.cur.execute(
            "INSERT INTO countries (country) VALUES (%s)",
            (country,),
        )
        self.conn.commit()

    def insert_all_aeroplanes(self, states):
        """states: список объектов StateVector"""
        for s in states:
            self.cur.execute(
                """
                INSERT INTO aircrafts
                (icao24, callsign, origin_country, baro_altitude, geo_altitude, velocity, on_ground)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (s.icao24, s.callsign, s.origin_country,
                 s.baro_altitude, s.geo_altitude, s.velocity, s.on_ground),
            )
        self.conn.commit()

    # ---------- SELECT ----------

    def get_countries_and_aeroplanes_count(self):
        """Список стран и количество самолётов в их воздушном пространстве."""
        self.cur.execute(
            """
            SELECT origin_country, COUNT(*)
            FROM aircrafts
            WHERE origin_country IS NOT NULL
            GROUP BY origin_country
            ORDER BY COUNT(*) DESC
            """
        )
        return self.cur.fetchall()

    def get_all_aeroplanes(self):
        """Список всех воздушных судов."""
        self.cur.execute("SELECT * FROM aircrafts")
        return self.cur.fetchall()

    def get_avg_speed(self):
        """Средняя скорость по всем самолётам."""
        self.cur.execute("SELECT AVG(velocity) FROM aircrafts WHERE velocity IS NOT NULL")
        result = self.cur.fetchone()
        return result[0] if result and result[0] is not None else 0.0

    def get_aeroplanes_with_higher_speed(self):
        """Самолёты, у которых скорость выше средней."""
        self.cur.execute("""
            SELECT * FROM aircrafts
            WHERE velocity > (SELECT AVG(velocity) FROM aircrafts)
        """)
        return self.cur.fetchall()

    def get_aeroplanes_with_keyword(self, keyword):
        """Самолёты, в позывном которых есть подстрока (например, 'ACA')."""
        self.cur.execute(
            "SELECT * FROM aircrafts WHERE callsign LIKE %s",
            (f"%{keyword}%",)
        )
        return self.cur.fetchall()

    def close(self):
        self.cur.close()
        self.conn.close()
