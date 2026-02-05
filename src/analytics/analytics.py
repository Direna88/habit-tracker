from __future__ import annotations

from datetime import datetime

from src.models.habit import Habit
from src.models.completion import Completion


def all_habits(habits: list[Habit]) -> list[Habit]:
    """Return all currently tracked habits."""
    return list(habits)


def habits_by_periodicity(habits: list[Habit], periodicity: str) -> list[Habit]:
    """Return habits that share the same periodicity."""
    return list(filter(lambda h: h.periodicity == periodicity, habits))


def _period_id(created_at: datetime, period_days: int, ts: datetime) -> int:
    """Map a timestamp to a 0-based period index starting from habit creation date."""
    delta_days = (ts.date() - created_at.date()).days
    return -1 if delta_days < 0 else delta_days // period_days


def longest_streak_for(habit: Habit, completions: list[Completion]) -> int:
    """
    Longest run streak for a given habit:
    - Each period counts as completed if at least one completion exists in that period.
    - Multiple completions in the same period count once.
    """
    period_days = habit.period_length_days()

    # map completions → period ids, filter negatives, de-duplicate, sort
    pids = sorted(
        set(
            filter(
                lambda p: p >= 0,
                map(
                    lambda c: _period_id(habit.created_at, period_days, c.completed_at),
                    filter(lambda c: c.habit_id == habit.id, completions),
                ),
            )
        )
    )

    if not pids:
        return 0

    best = 1
    run = 1
    for prev, curr in zip(pids, pids[1:]):
        run = run + 1 if curr == prev + 1 else 1
        best = max(best, run)
    return best


def longest_streak_overall(habits: list[Habit], completions: list[Completion]) -> tuple[Habit | None, int]:
    """Return the habit with the longest streak and its streak length."""
    if not habits:
        return (None, 0)

    streaks = list(map(lambda h: (h, longest_streak_for(h, completions)), habits))
    return max(streaks, key=lambda x: x[1])
