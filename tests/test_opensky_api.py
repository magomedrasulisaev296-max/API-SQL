from unittest.mock import MagicMock, patch

from opensky_api import OpenSkyApi, TokenManager


def make_response(status_code=200, payload=None):
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = payload if payload is not None else {}
    return response


@patch("opensky_api.requests.Session")
def test_get_states_success(mock_session_cls):
    session = MagicMock()
    session.get.return_value = make_response(
        payload={"time": 1700000000, "states": [["abc", "DLH", "Germany"]]}
    )
    mock_session_cls.return_value = session

    api = OpenSkyApi()
    result = api.get_states(bbox=(45, 55, 5, 15))

    assert result is not None
    assert result.time == 1700000000
    assert len(result.states) == 1
    assert result.states[0].icao24 == "abc"

    _, kwargs = session.get.call_args
    assert kwargs["params"] == {"lamin": 45, "lamax": 55, "lomin": 5, "lomax": 15}
    assert "Authorization" not in kwargs["headers"]


@patch("opensky_api.requests.Session")
def test_get_states_empty(mock_session_cls):
    session = MagicMock()
    session.get.return_value = make_response(payload={"states": None})
    mock_session_cls.return_value = session

    result = OpenSkyApi().get_states()

    assert result is not None
    assert result.states is None


@patch("opensky_api.requests.Session")
def test_get_states_error(mock_session_cls):
    session = MagicMock()
    session.get.return_value = make_response(status_code=429)
    mock_session_cls.return_value = session

    assert OpenSkyApi().get_states() is None


@patch("opensky_api.requests.Session")
def test_get_states_with_token(mock_session_cls):
    session = MagicMock()
    session.get.return_value = make_response(payload={"states": []})
    mock_session_cls.return_value = session

    tm = TokenManager(client_id="id", client_secret="secret")
    tm._access_token = "my-token"

    OpenSkyApi(token_manager=tm).get_states()

    _, kwargs = session.get.call_args
    assert kwargs["headers"]["Authorization"] == "Bearer my-token"


@patch("opensky_api.requests.post")
def test_token_manager_requests_token(mock_post):
    mock_post.return_value = make_response(
        payload={"access_token": "new-token", "expires_in": 1800}
    )

    tm = TokenManager(client_id="id", client_secret="secret")
    assert tm.get_token() == "new-token"
    mock_post.assert_called_once()
