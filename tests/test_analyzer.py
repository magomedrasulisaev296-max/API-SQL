from unittest.mock import MagicMock
from src.analyzer import Analyzer


def make_state(country="Germany", velocity=100.0, callsign="DLH123"):
    s = MagicMock()
    s.origin_country = country
    s.velocity = velocity
    s.callsign = callsign
    return s


def test_get_countries_and_aeroplanes_count():
    states = [
        make_state("Germany"),
        make_state("Germany"),
        make_state("France"),
    ]
    analyzer = Analyzer(states)
    assert analyzer.get_countries_and_aeroplanes_count() == {"Germany": 2, "France": 1}


def test_get_all_aeroplanes():
    states = [make_state(), make_state()]
    analyzer = Analyzer(states)
    assert analyzer.get_all_aeroplanes() == states


def test_get_avg_speed():
    states = [
        make_state(velocity=100.0),
        make_state(velocity=200.0),
        make_state(velocity=None),
    ]
    analyzer = Analyzer(states)
    assert analyzer.get_avg_speed() == 150.0


def test_get_avg_speed_empty():
    analyzer = Analyzer([])
    assert analyzer.get_avg_speed() == 0.0


def test_get_aeroplanes_with_higher_speed():
    states = [
        make_state(velocity=250.0),
        make_state(velocity=150.0),
        make_state(velocity=None),
    ]
    analyzer = Analyzer(states)
    result = analyzer.get_aeroplanes_with_higher_speed(200)
    assert len(result) == 1
    assert result[0].velocity == 250.0


def test_get_aeroplanes_with_keyword():
    states = [
        make_state(callsign="DLH123"),
        make_state(callsign="AFL456"),
        make_state(callsign=None),
    ]
    analyzer = Analyzer(states)
    result = analyzer.get_aeroplanes_with_keyword("dlh")
    assert len(result) == 1
    assert result[0].callsign == "DLH123"