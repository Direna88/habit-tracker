from __future__ import annotations

"""Tests for habit creation and uniqueness rules.

These tests exercise `DbHandler` behavior around creating habits
for specific users and enforcing the unique constraint on habit names.
"""


from pathlib import Path
from datetime import datetime
import sqlite3
import pytest

from src.database.db_handler import DbHandler


def test_create_habit_for_specific_user(tmp_path: Path) -> None:
    db = DbHandler(tmp_path / "t.db")
    u1 = db.create_user("u1")
    u2 = db.create_user("u2")

    db.create_habit("H1", "d", "daily", user_id=u1.id)
    db.create_habit("H2", "d", "weekly", user_id=u2.id)

    habits_u1 = db.list_habits(user_id=u1.id)
    habits_u2 = db.list_habits(user_id=u2.id)

    assert [h.name for h in habits_u1] == ["H1"]
    assert [h.name for h in habits_u2] == ["H2"]


def test_habit_name_unique_constraint(tmp_path: Path) -> None:
    db = DbHandler(tmp_path / "t.db")
    u = db.create_user("u1")

    db.create_habit("UniqueHabit", "d", "daily", user_id=u.id)

    with pytest.raises(sqlite3.IntegrityError):
        db.create_habit("UniqueHabit", "d2", "weekly", user_id=u.id)

def test_update_habit(tmp_path: Path) -> None:
    db = DbHandler(tmp_path / "t.db")
    u = db.create_user("u1")

    h = db.create_habit("OldName", "desc", "daily", user_id=u.id)

    updated = db.update_habit(
        h.id,
        name="NewName",
        periodicity="weekly",
    )

    assert updated is not None
    assert updated.name == "NewName"
    assert updated.periodicity == "weekly"
