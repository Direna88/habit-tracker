"""Unit tests for analytics functions.

These tests operate purely on model objects and validate the
calculation of streaks across daily and weekly periods.
"""

from datetime import datetime, timedelta

from src.models.habit import Habit
from src.models.completion import Completion
from src.analytics.analytics import (
    all_habits,
    habits_by_periodicity,
    longest_streak_for,
    longest_streak_overall,
    habits_due_today,
    longest_streaks_per_habit,
)


def test_all_habits_returns_copy() -> None:
    created = datetime(2025, 1, 1, 10, 0, 0)
    habits = [
        Habit(1, "A", "x", "daily", created),
        Habit(2, "B", "y", "weekly", created),
    ]
    out = all_habits(habits)
    assert out == habits
    assert out is not habits  # should be a new list


def test_habits_by_periodicity_filters_daily() -> None:
    created = datetime(2025, 1, 1, 10, 0, 0)
    habits = [
        Habit(1, "Daily1", "x", "daily", created),
        Habit(2, "Weekly1", "y", "weekly", created),
        Habit(3, "Daily2", "z", "daily", created),
    ]
    daily = habits_by_periodicity(habits, "daily")
    assert [h.id for h in daily] == [1, 3]


def test_longest_streak_daily_breaks_on_gap() -> None:
    created = datetime(2025, 1, 1, 10, 0, 0)
    h = Habit(1, "Daily", "x", "daily", created)

    comps = [
        Completion(None, 1, created + timedelta(days=0)),
        Completion(None, 1, created + timedelta(days=1)),
        Completion(None, 1, created + timedelta(days=2)),
        # gap day 3
        Completion(None, 1, created + timedelta(days=4)),
    ]
    assert longest_streak_for(h, comps) == 3


def test_longest_streak_counts_one_per_period() -> None:
    created = datetime(2025, 1, 1, 10, 0, 0)
    h = Habit(1, "Daily", "x", "daily", created)

    # two completions same day → still counts as 1 period
    comps = [
        Completion(None, 1, created + timedelta(hours=1)),
        Completion(None, 1, created + timedelta(hours=2)),
        Completion(None, 1, created + timedelta(days=1, hours=1)),
    ]
    assert longest_streak_for(h, comps) == 2


def test_longest_streak_weekly_counts_one_per_period() -> None:
    created = datetime(2025, 1, 1, 10, 0, 0)
    h = Habit(1, "Weekly", "x", "weekly", created)

    # Two completions in the same week (period 0) must count only once.
    comps = [
        Completion(None, 1, created + timedelta(days=1)),  # week 0
        Completion(None, 1, created + timedelta(days=2)),  # still week 0
        Completion(None, 1, created + timedelta(days=8)),  # week 1
    ]
    # Completed week 0 and week 1 consecutively -> streak is 2 periods
    assert longest_streak_for(h, comps) == 2


def test_longest_streak_weekly() -> None:
    created = datetime(2025, 1, 1, 10, 0, 0)
    h = Habit(1, "Weekly", "x", "weekly", created)

    comps = [
        Completion(None, 1, created + timedelta(days=1)),   # week 0
        Completion(None, 1, created + timedelta(days=8)),   # week 1
        Completion(None, 1, created + timedelta(days=15)),  # week 2
    ]
    assert longest_streak_for(h, comps) == 3


def test_longest_streak_overall_returns_habit_with_max_streak() -> None:
    created = datetime(2025, 1, 1, 10, 0, 0)

    h1 = Habit(1, "Daily", "x", "daily", created)
    h2 = Habit(2, "Weekly", "y", "weekly", created)

    # h1 streak = 2 (days 0,1)
    # h2 streak = 3 (weeks 0,1,2)
    comps = [
        Completion(None, 1, created + timedelta(days=0)),
        Completion(None, 1, created + timedelta(days=1)),
        Completion(None, 2, created + timedelta(days=1)),
        Completion(None, 2, created + timedelta(days=8)),
        Completion(None, 2, created + timedelta(days=15)),
    ]

    habit, streak = longest_streak_overall([h1, h2], comps)
    assert habit is not None
    assert habit.id == 2
    assert streak == 3


def test_longest_streak_overall_empty_habits() -> None:
    habit, streak = longest_streak_overall([], [])
    assert habit is None
    assert streak == 0


def test_longest_streaks_per_habit_returns_rows() -> None:
    created = datetime(2025, 1, 1, 10, 0, 0)
    h1 = Habit(1, "A", "x", "daily", created)
    h2 = Habit(2, "B", "y", "daily", created)

    comps = [
        Completion(None, 1, created + timedelta(days=0)),
        Completion(None, 1, created + timedelta(days=1)),  # h1 streak 2
        Completion(None, 2, created + timedelta(days=0)),  # h2 streak 1
    ]

    rows = longest_streaks_per_habit([h1, h2], comps)
    as_dict = {h.id: s for h, s in rows}
    assert as_dict == {1: 2, 2: 1}


def test_habits_due_today_returns_due_habits() -> None:
    created = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
    h1 = Habit(1, "DailyDue", "x", "daily", created)
    h2 = Habit(2, "DailyDone", "y", "daily", created)

    # Mark h2 as completed "now" so it is not due in current period
    comps = [Completion(None, 2, datetime.now())]

    due = habits_due_today([h1, h2], comps)
    assert [h.id for h in due] == [1]