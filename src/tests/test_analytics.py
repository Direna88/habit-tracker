from datetime import datetime, timedelta

from src.models.habit import Habit
from src.models.completion import Completion
from src.analytics.analytics import longest_streak_for


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


def test_longest_streak_weekly() -> None:
    created = datetime(2025, 1, 1, 10, 0, 0)
    h = Habit(1, "Weekly", "x", "weekly", created)

    comps = [
        Completion(None, 1, created + timedelta(days=1)),   # week 0
        Completion(None, 1, created + timedelta(days=8)),   # week 1
        Completion(None, 1, created + timedelta(days=15)),  # week 2
    ]
    assert longest_streak_for(h, comps) == 3
