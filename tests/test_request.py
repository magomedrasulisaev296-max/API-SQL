from unittest.mock import patch, MagicMock
from src.request import main


@patch("src.request.get_country_coords")
def test_coords_not_found(mock_coords, capsys):
    mock_coords.return_value = None
    main()
    captured = capsys.readouterr()
    assert "Не удалось получить координаты" in captured.out


@patch("src.request.OpenSkyApi")
@patch("src.request.TokenManager")
@patch("src.request.os.path.exists")
@patch("src.request.get_country_coords")
def test_with_credentials(mock_coords, mock_exists, mock_tm, mock_api, capsys):
    mock_coords.return_value = {"lat": "50.0", "lon": "10.0"}
    mock_exists.return_value = True

    mock_states = MagicMock()
    mock_states.states = []
    mock_api.return_value.__enter__.return_value.get_states.return_value = mock_states

    main()

    captured = capsys.readouterr()
    assert "Authenticated with credentials file" in captured.out
    assert "No states received" in captured.out


@patch("src.request.OpenSkyApi")
@patch("src.request.os.path.exists")
@patch("src.request.get_country_coords")
def test_anonymous_access(mock_coords, mock_exists, mock_api, capsys):
    mock_coords.return_value = {"lat": "50.0", "lon": "10.0"}
    mock_exists.return_value = False

    mock_states = MagicMock()
    mock_states.states = []
    mock_api.return_value.__enter__.return_value.get_states.return_value = mock_states

    main()

    captured = capsys.readouterr()
    assert "anonymous access" in captured.out


@patch("src.request.OpenSkyApi")
@patch("src.request.os.path.exists")
@patch("src.request.get_country_coords")
def test_with_states(mock_coords, mock_exists, mock_api, capsys):
    mock_coords.return_value = {"lat": "50.0", "lon": "10.0"}
    mock_exists.return_value = False

    s = MagicMock()
    s.icao24 = "abc123"
    s.callsign = "DLH123"
    s.origin_country = "Germany"
    s.baro_altitude = 10000
    s.geo_altitude = 10500
    s.on_ground = False

    mock_states = MagicMock()
    mock_states.states = [s]
    mock_api.return_value.__enter__.return_value.get_states.return_value = mock_states

    main()

    captured = capsys.readouterr()
    assert "abc123" in captured.out
    assert "DLH123" in captured.out
    assert "airborne" in captured.out