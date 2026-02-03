from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Completion:
    """
    A single check-off event for a habit.

    Multiple check-offs within the same period still count only once for streak evaluation.
    """

    id: int | None
    habit_id: int
    completed_at: datetime
