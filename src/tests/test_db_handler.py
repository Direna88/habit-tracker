from __future__ import annotations

"""Tests covering DbHandler integration behaviors.

These tests use temporary DB files to validate seeding, persistence,
and deletion cascades implemented by `DbHandler`.
"""


from datetime import datetime, timedelta
from pathlib import Path

from src.database.db_handler import DbHandler


def test_seed_creates_required_habits(tmp_path: Path) -> None:
    db_file = tmp_path / "habits.db"
    db = DbHandler(db_file)

    db.seed_if_empty()
    habits = db.list_habits()

    # At least 5 habits, daily + weekly
    assert len(habits) == 5
    assert any(h.periodicity == "daily" for h in habits)
    assert any(h.periodicity == "weekly" for h in habits)


def test_completion_is_persisted(tmp_path: Path) -> None:
    db_file = tmp_path / "habits.db"
    db = DbHandler(db_file)

    db.seed_if_empty()
    habit = db.list_habits()[0]

    before = db.list_completions(habit_id=habit.id)  # type: ignore[arg-type]

    # Add a completion in a NEW period so it must be saved.
    # Using +2 days makes this test robust even if seed already added a completion today.
    when = datetime.now() + timedelta(days=2)
    saved = db.add_completion(habit.id, when=when)  # type: ignore[arg-type]

    after = db.list_completions(habit_id=habit.id)  # type: ignore[arg-type]

    assert saved is True
    assert len(after) == len(before) + 1
    assert after[-1].habit_id == habit.id
    assert isinstance(after[-1].completed_at, datetime)


def test_delete_habit_removes_completions(tmp_path: Path) -> None:
    db_file = tmp_path / "habits.db"
    db = DbHandler(db_file)

    db.seed_if_empty()
    habit = db.list_habits()[0]

    # ensure habit has completions
    initial = db.list_completions(habit_id=habit.id)  # type: ignore[arg-type]
    assert len(initial) > 0

    # delete habit
    db.delete_habit(habit.id)  # type: ignore[arg-type]

    # completions should be gone due to FK cascade
    remaining = db.list_completions(habit_id=habit.id)  # type: ignore[arg-type]
    assert remaining == []
