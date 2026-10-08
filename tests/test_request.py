from unittest.mock import MagicMock, patch

from src.request import get_states, main


@patch("src.request.requests.get")
def test_get_states_success(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"states": [["abc", "DLH", "Germany"]]}
    mock_get.return_value = mock_response

    result = get_states((45, 55, 5, 15))
    assert result == [["abc", "DLH", "Germany"]]


@patch("src.request.requests.get")
def test_get_states_empty(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"states": None}
    mock_get.return_value = mock_response

    assert get_states((45, 55, 5, 15)) == []


@patch("src.request.requests.get")
def test_get_states_error(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response

    assert get_states((45, 55, 5, 15)) == []


@patch("src.request.time.sleep")
@patch("src.request.DBManager")
@patch("src.request.get_country_coords")
@patch("src.request.get_states")
def test_main_with_data(mock_states, mock_coords, mock_db_cls, mock_sleep):
    mock_coords.return_value = {"lat": 50.0, "lon": 10.0}
    mock_states.return_value = [
        ["abc", "DLH123", "Germany", None, None, None, None, None, False, 250.0, None, None, None, 10000.0]
    ]

    mock_db = MagicMock()
    mock_db.get_all_aeroplanes.return_value = [
        (1, "abc", "DLH123", "Germany", 10000, 10000, 250.0, False)
    ]
    mock_db_cls.return_value = mock_db

    main()

    assert mock_db.insert_all_aeroplanes.called
    assert mock_db.insert_countries_and_counts.called
    mock_db.close.assert_called_once()


@patch("src.request.time.sleep")
@patch("src.request.DBManager")
@patch("src.request.get_country_coords")
def test_main_no_coords(mock_coords, mock_db_cls, mock_sleep, capsys):
    mock_coords.return_value = None
    mock_db = MagicMock()
    mock_db_cls.return_value = mock_db

    main()

    assert "Не удалось получить координаты" in capsys.readouterr().out
    mock_db.close.assert_called_once()
