from __future__ import annotations

"""
Habit domain model.

This module defines the `Habit` dataclass and the `Periodicity` type.
- `Periodicity` is intentionally a Literal to keep the domain explicit
    and avoid magic strings scattered throughout the codebase.
- `period_length_days()` centralizes the mapping from periodicity to
    a length in days so analytics and persistence logic share the same
    definition.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

Periodicity = Literal["daily", "weekly"]


@dataclass(frozen=True)
class Habit:
        id: int | None
        name: str
        description: str
        periodicity: Periodicity
        created_at: datetime

        def period_length_days(self) -> int:
                """Return the length of the habit period in days.

                We map `daily` -> 1 and `weekly` -> 7. Keeping this logic here
                ensures all callers (analytics, DB logic) agree on what a
                'period' means.
                """
                return 1 if self.periodicity == "daily" else 7
