from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Optional

import requests

STATES_URL = "https://opensky-network.org/api/states/all"
TOKEN_URL = (
    "https://auth.opensky-network.org/auth/realms/opensky-network/"
    "protocol/openid-connect/token"
)

# Порядок полей в ответе OpenSky /api/states/all.
FIELD_NAMES = (
    "icao24",
    "callsign",
    "origin_country",
    "time_position",
    "last_contact",
    "longitude",
    "latitude",
    "baro_altitude",
    "on_ground",
    "velocity",
    "true_track",
    "vertical_rate",
    "sensors",
    "geo_altitude",
    "squawk",
    "spi",
    "position_source",
)


@dataclass
class StateVector:
    """Состояние одного воздушного судна."""

    icao24: str
    callsign: Optional[str]
    origin_country: str
    time_position: Optional[int] = None
    last_contact: Optional[int] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    baro_altitude: Optional[float] = None
    on_ground: Optional[bool] = None
    velocity: Optional[float] = None
    true_track: Optional[float] = None
    vertical_rate: Optional[float] = None
    sensors: Optional[list] = None
    geo_altitude: Optional[float] = None
    squawk: Optional[str] = None
    spi: Optional[bool] = None
    position_source: Optional[int] = None

    @classmethod
    def from_row(cls, row: Iterable[Any]) -> "StateVector":
        """Собирает StateVector из «сырой» строки ответа API."""
        values = list(row)
        # Короткие строки дополняем None, длинные — обрезаем.
        if len(values) < len(FIELD_NAMES):
            values += [None] * (len(FIELD_NAMES) - len(values))
        data = dict(zip(FIELD_NAMES, values[: len(FIELD_NAMES)]))

        callsign = data["callsign"]
        if isinstance(callsign, str):
            data["callsign"] = callsign.strip() or None

        return cls(**data)


@dataclass
class StatesResponse:
    """Ответ /api/states/all: время снимка и список состояний."""

    time: Optional[int] = None
    states: Optional[list[StateVector]] = None


class TokenManager:
    """Получает и обновляет OAuth-токен OpenSky по client_id/client_secret."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        token_url: str = TOKEN_URL,
        timeout: float = 10.0,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.timeout = timeout
        self._access_token: Optional[str] = None
        self._expires_in: int = 0

    def get_token(self) -> str:
        if self._access_token is None:
            self._request_token()
        return self._access_token or ""

    def refresh(self) -> str:
        self._request_token()
        return self._access_token or ""

    def _request_token(self) -> None:
        response = requests.post(
            self.token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        self._access_token = payload.get("access_token")
        self._expires_in = int(payload.get("expires_in") or 0)


class OpenSkyApi:
    """Клиент OpenSky. Поддерживает использование как контекстного менеджера."""

    def __init__(
        self,
        token_manager: Optional[TokenManager] = None,
        base_url: str = STATES_URL,
        timeout: float = 30.0,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.token_manager = token_manager
        self.base_url = base_url
        self.timeout = timeout
        self.session = session or requests.Session()

    def __enter__(self) -> "OpenSkyApi":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.session.close()

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.token_manager is not None:
            headers["Authorization"] = f"Bearer {self.token_manager.get_token()}"
        return headers

    def get_states(
        self,
        bbox: Optional[tuple[float, float, float, float]] = None,
        icao24: Optional[str] = None,
        time: Optional[int] = None,
    ) -> Optional[StatesResponse]:
        """Возвращает StatesResponse или None при ошибке/лимите запросов."""
        params: dict[str, Any] = {}
        if bbox is not None:
            lamin, lamax, lomin, lomax = bbox
            params.update(lamin=lamin, lamax=lamax, lomin=lomin, lomax=lomax)
        if icao24 is not None:
            params["icao24"] = icao24
        if time is not None:
            params["time"] = time

        response = self.session.get(
            self.base_url,
            params=params,
            headers=self._headers(),
            timeout=self.timeout,
        )
        if response.status_code != 200:
            print(f"OpenSky error: {response.status_code}")
            return None

        payload = response.json() or {}
        raw_states = payload.get("states")
        states = (
            [StateVector.from_row(row) for row in raw_states]
            if raw_states
            else None
        )
        return StatesResponse(time=payload.get("time"), states=states)
