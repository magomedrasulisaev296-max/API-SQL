from unittest.mock import MagicMock, patch

from src.Classes import DBManager


def make_db():
    with patch("src.Classes.psycopg2.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur
        mock_connect.return_value = mock_conn
        db = DBManager()
        return db, mock_conn, mock_cur


def test_create_tables():
    db, mock_conn, mock_cur = make_db()
    assert mock_cur.execute.call_count == 2
    mock_conn.commit.assert_called_once()
    sql = " ".join(str(call[0][0]) for call in mock_cur.execute.call_args_list)
    assert "COUNT" not in sql
    assert "countries_count" not in sql
    assert "all_aircraft" not in sql


def test_insert_country():
    db, mock_conn, mock_cur = make_db()
    mock_cur.reset_mock()
    mock_conn.reset_mock()
    db.insert_country("Germany")
    mock_cur.execute.assert_called_once()
    mock_conn.commit.assert_called_once()


def test_insert_all_aeroplanes():
    db, mock_conn, mock_cur = make_db()
    mock_cur.reset_mock()
    mock_conn.reset_mock()

    s = MagicMock()
    s.icao24 = "abc"
    s.callsign = "DLH"
    s.origin_country = "Germany"
    s.baro_altitude = 10000
    s.geo_altitude = 10500
    s.velocity = 250.0
    s.on_ground = False

    db.insert_all_aeroplanes([s])
    mock_cur.execute.assert_called_once()
    mock_conn.commit.assert_called_once()


def test_get_countries_and_aeroplanes_count():
    db, mock_conn, mock_cur = make_db()
    mock_cur.fetchall.return_value = [("Germany", 2), ("France", 1)]
    result = db.get_countries_and_aeroplanes_count()
    assert result == [("Germany", 2), ("France", 1)]
    sql = mock_cur.execute.call_args[0][0]
    assert "COUNT(*)" in sql
    assert "aircrafts" in sql


def test_get_all_aeroplanes():
    db, mock_conn, mock_cur = make_db()
    mock_cur.fetchall.return_value = [("abc",), ("def",)]
    assert db.get_all_aeroplanes() == [("abc",), ("def",)]


def test_get_avg_speed():
    db, mock_conn, mock_cur = make_db()
    mock_cur.fetchone.return_value = (150.5,)
    assert db.get_avg_speed() == 150.5


def test_get_avg_speed_none():
    db, mock_conn, mock_cur = make_db()
    mock_cur.fetchone.return_value = (None,)
    assert db.get_avg_speed() == 0.0


def test_get_aeroplanes_with_higher_speed():
    db, mock_conn, mock_cur = make_db()
    mock_cur.fetchall.return_value = [("fast1",), ("fast2",)]
    assert len(db.get_aeroplanes_with_higher_speed()) == 2


def test_get_aeroplanes_with_keyword():
    db, mock_conn, mock_cur = make_db()
    mock_cur.fetchall.return_value = [("ACA123",)]
    assert db.get_aeroplanes_with_keyword("ACA") == [("ACA123",)]


def test_close():
    db, mock_conn, mock_cur = make_db()
    db.close()
    mock_cur.close.assert_called_once()
    mock_conn.close.assert_called_once()
