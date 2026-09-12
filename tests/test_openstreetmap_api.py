from unittest.mock import patch, MagicMock
from src.openstreetmapapi import get_country_coords


@patch("src.openstreetmapapi.requests.get")
def test_success(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"lat": "51.0", "lon": "10.0"}]
    mock_get.return_value = mock_response

    assert get_country_coords("Germany") == {"lat": 51.0, "lon": 10.0}


@patch("src.openstreetmapapi.requests.get")
def test_empty(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = []
    mock_get.return_value = mock_response

    assert get_country_coords("Neverland") is None


@patch("src.openstreetmapapi.requests.get")
def test_error(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response

    assert get_country_coords("Germany") is None