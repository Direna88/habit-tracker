from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

Periodicity = Literal["daily", "weekly"]


@dataclass(frozen=True)
class Habit:
    """
    Habit definition stored in the tracker.

    A habit is identified by its task (name/description) and a periodicity (daily/weekly).
    The created_at timestamp is used as the reference point for period-based streak evaluation.
    """

    id: int | None
    name: str
    description: str
    periodicity: Periodicity
    created_at: datetime

    def period_length_days(self) -> int:
        """Return the period length in days (1 for daily, 7 for weekly)."""
        return 1 if self.periodicity == "daily" else 7
