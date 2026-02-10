from __future__ import annotations

"""Tests for user creation and uniqueness behavior.

These tests verify that users can be created/listed and that the
database enforces a unique constraint on usernames.
"""


import sqlite3
import pytest
from pathlib import Path

from src.database.db_handler import DbHandler


def test_create_user_and_list(tmp_path: Path) -> None:
    db = DbHandler(tmp_path / "t.db")

    u = db.create_user("alice")
    assert u.id is not None
    assert u.username == "alice"

    users = db.list_users()
    assert len(users) == 1
    assert users[0].username == "alice"


def test_username_unique_constraint(tmp_path: Path) -> None:
    db = DbHandler(tmp_path / "t.db")
    db.create_user("alice")

    with pytest.raises(sqlite3.IntegrityError):
        db.create_user("alice")
