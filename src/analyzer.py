from __future__ import annotations

from typing import Any, Optional


class Analyzer:
    def __init__(self, states: Optional[list[Any]] = None) -> None:
        self.states = list(states or [])

    def get_all_aeroplanes(self) -> list[Any]:
        """Список всех воздушных судов."""
        return list(self.states)

    def get_countries_and_aeroplanes_count(self) -> dict[str, int]:
        """Словарь {страна: количество самолётов}."""
        counts: dict[str, int] = {}
        for state in self.states:
            country = getattr(state, "origin_country", None)
            if country:
                counts[country] = counts.get(country, 0) + 1
        return counts

    def get_avg_speed(self) -> float:
        """Средняя скорость по всем самолётам (0.0, если данных нет)."""
        speeds = [
            state.velocity
            for state in self.states
            if getattr(state, "velocity", None) is not None
        ]
        if not speeds:
            return 0.0
        return sum(speeds) / len(speeds)

    def get_aeroplanes_with_higher_speed(
        self, threshold: Optional[float] = None
    ) -> list[Any]:
        """Самолёты со скоростью выше порога.

        Если threshold не задан, используется средняя скорость по списку.
        """
        limit = self.get_avg_speed() if threshold is None else threshold
        return [
            state
            for state in self.states
            if getattr(state, "velocity", None) is not None
            and state.velocity > limit
        ]

    def get_aeroplanes_with_keyword(self, keyword: str) -> list[Any]:
        """Самолёты, в позывном которых есть подстрока (например, 'ACA')."""
        return [
            state
            for state in self.states
            if getattr(state, "callsign", None) and keyword in state.callsign
        ]
