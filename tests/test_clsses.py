from unittest.mock import patch, MagicMock
from src.Classes import DBmanager


@patch("src.Classes.psycopg2.connect")
def test_dbmanager(mock_connect):
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    mock_connect.return_value = mock_conn

    db = DBmanager()
    assert mock_cur.execute.call_count == 4

    db.insert_countries_and_counts({"Germany": 2})

    s = MagicMock()
    s.icao24 = "abc"
    s.callsign = "DLH"
    s.origin_country = "Germany"
    s.baro_altitude = 10000
    s.geo_altitude = 10500
    s.velocity = 250.0
    s.on_ground = False

    db.insert_all_aeroplanes([s])
    db.insert_avg_speed(150.0)
    db.insert_high_speed_aircraft([s])

    assert db.get_aeroplanes_with_keyword("DLH")

    db.close()
    mock_cur.close.assert_called_once()
    mock_conn.close.assert_called_once()