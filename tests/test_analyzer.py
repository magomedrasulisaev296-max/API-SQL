from src.Classes import DBManager
from src.analyzer import Analyzer
from opensky_api import OpenSkyApi, StateVector, TokenManager


class FakeState:
    def __init__(self, icao24, callsign, country, velocity):
        self.icao24 = icao24
        self.callsign = callsign
        self.origin_country = country
        self.velocity = velocity
        self.baro_altitude = 10000.0
        self.geo_altitude = 10500.0
        self.on_ground = False


def make_analyzer():
    return Analyzer(
        [
            FakeState("a1", "DLH123", "Germany", 250.0),
            FakeState("a2", "ACA456", "Canada", 150.0),
            FakeState("a3", None, "Germany", None),
        ]
    )


def test_get_all_aeroplanes():
    analyzer = make_analyzer()
    assert len(analyzer.get_all_aeroplanes()) == 3


def test_empty_analyzer():
    analyzer = Analyzer()
    assert analyzer.get_all_aeroplanes() == []
    assert analyzer.get_countries_and_aeroplanes_count() == {}
    assert analyzer.get_avg_speed() == 0.0


def test_get_countries_and_aeroplanes_count():
    counts = make_analyzer().get_countries_and_aeroplanes_count()
    assert counts == {"Germany": 2, "Canada": 1}


def test_get_avg_speed_ignores_none():
    assert make_analyzer().get_avg_speed() == 200.0


def test_get_aeroplanes_with_higher_speed_uses_average():
    fast = make_analyzer().get_aeroplanes_with_higher_speed()
    assert [s.icao24 for s in fast] == ["a1"]


def test_get_aeroplanes_with_higher_speed_threshold():
    fast = make_analyzer().get_aeroplanes_with_higher_speed(threshold=100)
    assert [s.icao24 for s in fast] == ["a1", "a2"]


def test_get_aeroplanes_with_keyword():
    found = make_analyzer().get_aeroplanes_with_keyword("ACA")
    assert [s.icao24 for s in found] == ["a2"]


def test_get_aeroplanes_with_keyword_handles_none_callsign():
    assert make_analyzer().get_aeroplanes_with_keyword("XYZ") == []


def test_opensky_state_vector_from_row():
    row = [
        "abc", "DLH123 ", "Germany", 1700000000, 1700000001,
        10.5, 51.2, 10000.0, False, 250.0, 90.0, -2.0,
        [1], 10500.0, "1234", False, 0,
    ]
    sv = StateVector.from_row(row)
    assert sv.icao24 == "abc"
    assert sv.callsign == "DLH123"
    assert sv.origin_country == "Germany"
    assert sv.baro_altitude == 10000.0
    assert sv.geo_altitude == 10500.0
    assert sv.velocity == 250.0
    assert sv.on_ground is False


def test_opensky_state_vector_short_row():
    sv = StateVector.from_row(["abc", "DLH", "Germany"])
    assert sv.velocity is None
    assert sv.geo_altitude is None


def test_token_manager_get_token():
    tm = TokenManager(client_id="id", client_secret="secret")
    tm._access_token = "token"
    assert tm.get_token() == "token"


def test_open_sky_api_context_manager():
    with OpenSkyApi() as api:
        assert isinstance(api, OpenSkyApi)


def test_db_manager_class_name():
    assert DBManager.__name__ == "DBManager"
