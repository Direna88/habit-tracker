from __future__ import annotations

"""Tests for completion rules and cascade behavior.

Verifies that only one completion per logical period is accepted
and that deleting users cascades to remove related habits and completions.
"""


from datetime import datetime, timedelta
from pathlib import Path

from src.database.db_handler import DbHandler


def test_one_completion_per_period_daily(tmp_path: Path) -> None:
    db = DbHandler(tmp_path / "t.db")
    u = db.create_user("u1")

    created = datetime(2025, 1, 1, 10, 0, 0)
    h = db.create_habit("DailyHabit", "d", "daily", created_at=created, user_id=u.id)

    # same day (same period) -> only first should save
    assert db.add_completion(h.id, when=created + timedelta(hours=1)) is True  # type: ignore[arg-type]
    assert db.add_completion(h.id, when=created + timedelta(hours=5)) is False  # type: ignore[arg-type]

    # next day -> new period -> saves
    assert db.add_completion(h.id, when=created + timedelta(days=1, hours=1)) is True  # type: ignore[arg-type]


def test_user_delete_cascades_habits_and_completions(tmp_path: Path) -> None:
    db = DbHandler(tmp_path / "t.db")
    u = db.create_user("u1")

    h = db.create_habit("H", "d", "daily", user_id=u.id)
    db.add_completion(h.id)  # type: ignore[arg-type]

    assert len(db.list_habits(user_id=u.id)) == 1
    assert len(db.list_completions(habit_id=h.id)) == 1  # type: ignore[arg-type]

    db.delete_user(u.id)

    # habits gone
    assert db.list_habits(user_id=u.id) == []
    # completions gone (habit FK cascade first, then completion FK)
    assert db.list_completions(habit_id=h.id) == []  # type: ignore[arg-type]
