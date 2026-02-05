from datetime import datetime
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
    db.add_completion(habit.id)  # type: ignore[arg-type]
    after = db.list_completions(habit_id=habit.id)  # type: ignore[arg-type]

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
