from unittest.mock import patch, MagicMock
from src.request import main


@patch("src.request.get_country_coords")
def test_coords_not_found(mock_coords, capsys):
    mock_coords.return_value = None
    main()
    assert "Не удалось получить координаты" in capsys.readouterr().out


@patch("src.request.load_dotenv")
@patch("src.request.os.getenv")
@patch("src.request.OpenSkyApi")
@patch("src.request.TokenManager")
@patch("src.request.get_country_coords")
def test_with_credentials(mock_coords, mock_tm, mock_api, mock_getenv, mock_dotenv, capsys):
    mock_coords.return_value = {"lat": "50.0", "lon": "10.0"}
    mock_getenv.side_effect = lambda k: {"CLIENT_ID": "id", "CLIENT_SECRET": "secret"}.get(k)

    mock_states = MagicMock()
    mock_states.states = []
    mock_api.return_value.__enter__.return_value.get_states.return_value = mock_states

    main()
    assert "Authenticated with .env credentials" in capsys.readouterr().out


@patch("src.request.load_dotenv")
@patch("src.request.os.getenv")
@patch("src.request.OpenSkyApi")
@patch("src.request.get_country_coords")
def test_no_credentials(mock_coords, mock_api, mock_getenv, mock_dotenv, capsys):
    mock_coords.return_value = {"lat": "50.0", "lon": "10.0"}
    mock_getenv.return_value = None

    mock_states = MagicMock()
    mock_states.states = []
    mock_api.return_value.__enter__.return_value.get_states.return_value = mock_states

    main()
    assert "No credentials found in .env" in capsys.readouterr().out